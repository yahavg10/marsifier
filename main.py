import yaml

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import container
from src.database.database import DataBase
from src.pipeline_runner.pipeline_runner import PipelineRunner
from src.pipeline_runner.pipeline_utils import get_united_name
from src.receiver.receiver import Receiver
from src.utils.file_utils import setup_logger, load_configuration
from src.utils.function_utils import get_receivers


def main():
    setup_logger()
    app_config = load_configuration(AppConfig, yaml.safe_load)
    container.register(AppConfig, fn_init=load_configuration,
                       config_model=AppConfig,
                       load_conf_fn=yaml.safe_load)
    container.register(Receiver, data_source_handlers=get_receivers(app_config))
    container.register(DataBase, databases_directory=app_config.databases.get("directory"))
    container.register(PipelineRunner, config_module=app_config.pipeline["config_module"],
                       steps_module=app_config.pipeline["steps_module"])

    database, pipeline = container.get_services("DataBase", "PipelineRunner")

    database.setup_all_databases()
    database.write(key=pipeline.run_pipeline("C:/Users/nadav/Desktop/all_images/image12_a.jpg"),

                   expiry=60,
                   value="test")


if __name__ == "__main__":
    main()
