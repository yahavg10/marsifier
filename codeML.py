import os
import re
import statistics
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import numpy as np
from joblib import dump, load
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression

# -------------------------
# Config
# -------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "projects")
MODEL_DIR = os.getenv("MODEL_DIR", "./models")  # where anomaly.joblib / nextop.joblib live
os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------
# Minimal domain model
# -------------------------
class ChangeRequest(BaseModel):
    project: str
    change_no_1: Optional[str] = None
    change_no_2: Optional[str] = None
    change_no_3: Optional[str] = None

# -------------------------
# Mongo repository
# -------------------------
class Repo:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.changes = self.db["operations_log"]  # expects documents with {"project","operation","timestamp","project_size"}
        self.projects = self.db["projects"]

    def history(self, project: str, limit: int = 1000):
        return list(self.changes.find({"project": project}).sort("timestamp", -1).limit(limit))

    def project_size(self, project: str):
        p = self.projects.find_one({"project": project}) or {}
        return len(p.get("destinations", []))

# -------------------------
# Parser + feature builder
# -------------------------
_op_pat = re.compile(r"\[(.*?)\]")
def parse_change_text(txt: Optional[str]):
    if not txt: return {}
    op = "unknown"
    txt_low = txt.lower()
    if "add" in txt_low: op = "add"
    elif "delete" in txt_low: op = "delete"
    elif "update" in txt_low: op = "update"
    items = _op_pat.findall(txt)
    targets = [i.strip() for i in items[0].split(",")] if items else []
    return {"operation": op, "targets": targets}

def build_features(changes: List[dict], history: List[dict], project_size: int):
    adds = sum(1 for c in changes if c["operation"] == "add")
    deletes = sum(1 for c in changes if c["operation"] == "delete")
    updates = sum(1 for c in changes if c["operation"] == "update")
    total_ops = adds + deletes + updates
    recent_count = sum(1 for h in history if h.get("timestamp") and
                       h["timestamp"] >= datetime.utcnow() - timedelta(days=1))
    hr = datetime.utcnow().hour
    wd = datetime.utcnow().weekday()
    avg_daily = _avg_daily_ops(history)
    return {
        "adds": adds, "deletes": deletes, "updates": updates,
        "total_ops": total_ops, "recent_24h": recent_count,
        "project_size": project_size, "hour": hr, "weekday": wd,
        "avg_daily_ops": avg_daily
    }

def _avg_daily_ops(history):
    if not history: return 0.0
    # count ops per day over last 30 days
    cutoff = datetime.utcnow() - timedelta(days=30)
    days = {}
    for h in history:
        ts = h.get("timestamp")
        if not ts or ts < cutoff: continue
        key = ts.date().isoformat()
        days[key] = days.get(key, 0) + 1
    return statistics.mean(days.values()) if days else 0.0

# -------------------------
# Pluggable ML: load or train
# -------------------------
def model_paths():
    return os.path.join(MODEL_DIR, "anomaly.joblib"), os.path.join(MODEL_DIR, "nextop.joblib")

def load_or_train(repo: Repo):
    a_path, n_path = model_paths()
    # load anomaly
    if os.path.exists(a_path):
        anomaly = load(a_path)
    else:
        anomaly = _train_anomaly(repo)
        dump(anomaly, a_path)
    # load next-op classifier
    if os.path.exists(n_path):
        nextop = load(n_path)
    else:
        nextop = _train_nextop(repo)
        dump(nextop, n_path)
    return anomaly, nextop

def _history_vectors(repo: Repo):
    # builds X (features) and y (operation label)
    docs = list(repo.changes.find().limit(50000))
    X, y = [], []
    for d in docs:
        ts = d.get("timestamp")
        hr = ts.hour if ts else 12
        wd = ts.weekday() if ts else 0
        size = d.get("project_size", 0)
        op = d.get("operation", "unknown")
        vec = [hr, wd, size,
               1 if op == "add" else 0,
               1 if op == "delete" else 0,
               1 if op == "update" else 0]
        X.append(vec); y.append(op)
    return np.array(X) if X else np.zeros((0,6)), y

def _train_anomaly(repo: Repo):
    X, y = _history_vectors(repo)
    # if not enough data, create a trivial IsolationForest that returns neutral scores
    if X.shape[0] < 5:
        return IsolationForest(contamination=0.1).fit(np.zeros((10, X.shape[1] if X.shape[1] else 1)))
    return IsolationForest(contamination=0.05, random_state=42).fit(X)

def _train_nextop(repo: Repo):
    X, y = _history_vectors(repo)
    if X.shape[0] < 10 or len(set(y)) <= 1:
        # fallback dumb classifier mapping majority to 'update'
        clf = LogisticRegression()
        # train on small synthetic data
        X_synth = np.array([[12,0,1,1,0,0],[12,0,1,0,1,0],[12,0,1,0,0,1]])
        y_synth = ["add","delete","update"]
        return LogisticRegression().fit(X_synth, y_synth)
    return LogisticRegression(max_iter=1000).fit(X, y)

# -------------------------
# Analysis helpers
# -------------------------
def explain_anomaly(score):
    # IsolationForest.decision_function: higher = normal, lower = anomaly
    # normalize into [-1,1] by clipping
    s = float(score)
    if s < -0.5:
        return "Highly unusual timing/volume for this project."
    if s < -0.1:
        return "Somewhat unusual compared to project history."
    return "Consistent with historical activity."

def behavior_category_from_score(score):
    if score > 0.5: return "aggressive_modification"
    if score > 0.1: return "elevated_change_activity"
    if score > -0.1: return "normal_usage"
    return "low_activity"

def intent_from_ops(feat):
    rules = [
        (lambda f: f["adds"] >= 2, "expanding_project"),
        (lambda f: f["deletes"] >= 2, "cleanup_unused_destinations"),
        (lambda f: f["updates"] >= 2, "optimizing_routes"),
        (lambda f: f["adds"]>0 and f["deletes"]>0, "migrating_to_new_schema"),
        (lambda f: f["updates"]==1 and f["adds"]==0 and f["deletes"]==0, "fixing_broken_state"),
    ]
    for cond, lab in rules:
        if cond(feat): return lab
    return "general_modification"

def risk_from(intent, category):
    if category == "aggressive_modification": return "high"
    if intent in ("migrating_to_new_schema","cleanup_unused_destinations"): return "medium"
    return "low"

# -------------------------
# FastAPI wiring
# -------------------------
app = FastAPI(title="ML Project Behavior Analyzer - pluggable")

repo = Repo()
anomaly_model, nextop_model = load_or_train(repo)  # load or train at startup

@app.post("/analyze")
def analyze(req: ChangeRequest):
    # parse changes
    changes = []
    for field in ("change_no_1","change_no_2","change_no_3"):
        txt = getattr(req, field)
        parsed = parse_change_text(txt)
        if parsed: changes.append(parsed)

    history = repo.history(req.project, limit=1000)
    size = repo.project_size(req.project)
    feat = build_features(changes, history, size)

    # prepare vector for models (same format as training)
    X = np.array([[feat["hour"], feat["weekday"], feat["project_size"],
                   feat["adds"], feat["deletes"], feat["updates"]]])
    # anomaly: use decision_function -> lower = more anomalous
    try:
        raw_anom = anomaly_model.decision_function(X)[0]
    except Exception:
        raw_anom = -0.0
    anom_expl = explain_anomaly(raw_anom)

    # behavior score: invert anomaly to positive meaning more activity if anomaly high negative? 
    # We'll craft a simple combined score: normalized adds+deletes+updates scaled by anomaly inverse
    activity = feat["total_ops"]
    avg = feat["avg_daily_ops"] or 1.0
    activity_score = (activity - avg) / (avg if avg else 1.0)
    behavior_score = float(round(activity_score + (-raw_anom), 2))

    # predict next op
    try:
        nextop = nextop_model.predict(X)[0]
    except Exception:
        nextop = "update"

    intent = intent_from_ops(feat)
    category = behavior_category_from_score(behavior_score)
    risk = risk_from(intent, category)

    # human-friendly strings
    change_summary = f"Added {feat['adds']}, removed {feat['deletes']}, updated {feat['updates']}."
    historical_compare = ("No historical data." if not history else
                          f"Avg daily ops: {round(feat['avg_daily_ops'],2)}; recent 24h: {feat['recent_24h']}")

    return {
        "project": req.project,
        "behavior_score": behavior_score,
        "behavior_category": category,
        "predicted_next_operation": nextop,
        "detected_intent": intent,
        "risk_level": risk,
        "change_summary": change_summary,
        "anomaly_explanation": anom_expl,
        "historical_comparison": historical_compare,
        "raw_anomaly_score": float(raw_anom)
    }