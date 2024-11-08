import yaml

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import container
from src.database.database import DataBase
from src.pipeline_runner import pipeline_utils
from src.pipeline_runner.pipeline_runner import PipelineRunner
from src.receiver.receiver import Receiver
from src.sender import sender
from src.utils.file_utils import setup_logger, load_configuration
from src.utils.function_utils import get_receivers


def initial_register_services():
    app_config = load_configuration(AppConfig, yaml.safe_load)

    container.register_functions_in_module(pipeline_utils)
    container.register_functions_in_module(sender)

    container.register(AppConfig, fn_init=load_configuration,
                       config_model=AppConfig,
                       load_conf_fn=yaml.safe_load)

    container.register(PipelineRunner, config_module=app_config.pipeline["config_module"],
                       steps_module=app_config.pipeline["steps_module"])

    container.register(DataBase, databases_directory=app_config.databases.get("directory"))

    container.register(Receiver, data_source_handlers=get_receivers(app_config))


def main():
    setup_logger()
    initial_register_services()

    receiver, database, pipeline = container.get_services("Receiver", "DataBase", "PipelineRunner")

    try:
        database.setup_all_databases()
    finally:
        receiver.start()


if __name__ == "__main__":
    main()
