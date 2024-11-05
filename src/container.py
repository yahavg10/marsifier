from configurations.config_models.app_model import AppConfig
from src.database.database import DataBase
from src.pipeline_runner.pipeline_runner import PipelineRunner
from src.receiver.receiver import Receiver
from src.utils.function_utils import import_dynamic_model


class IoCContainer:
    def __init__(self, config: AppConfig):
        self.config = config
        self.receiver = Receiver
        self.database = DataBase
        self.pipeline = PipelineRunner

    def configure(self):
        self.receiver = Receiver(self.get_receivers())
        self.database = DataBase(self.config.databases.get("directory"))
        self.pipeline = PipelineRunner(config_module="configurations.developer_config",
                                                    steps_module="src.pipeline_runner.pipeline_utils")

    def get_receivers(self):
        receivers = {}
        for receiver_name, receiver_conf in self.config.receivers.items():
            receiver_model = import_dynamic_model(receiver_conf["path"])
            receivers[receiver_name] = receiver_model(**receiver_conf["conf"])
        return receivers
