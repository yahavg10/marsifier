import yaml

from configurations.config_models.app_model import AppConfig
from src.utils.file_utils import load_configuration

app_config = load_configuration(AppConfig, yaml.safe_load)

database_functions_template = ("get_instance_connection", "setup",
                               "connect", "disconnect",
                               "write", "fetch", "delete")

file_read_mode = "rb"

pipeline_steps = [
    {
        "name": "get_file_name"
    },
    {
        "name": "get_united_name",
        "config": {"suffixes": app_config.sender["file_invoker"]["suffixes"]}
    }
]


#     {
#         "name": "process_by_existence",
#         "config": {"folder_path": app_config.receivers["file"]["conf"]["folder_to_monitor"]}
#     }
