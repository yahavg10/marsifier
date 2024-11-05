from configurations.developer_config import app_config
from src.container import IoCContainer
from src.utils.file_utils import setup_logger


def main():
    setup_logger()
    container = IoCContainer(app_config)
    container.configure()
    container.database.setup_all_databases(app_config.databases["types"])
    container.database.write(database_name="redis_handler",
                             key="test",
                             expiry=60,
                             value="test_value")
    container.pipeline.run_pipeline("C:/Users/nadav/Desktop/all_images/image12_a.jpg")


if __name__ == "__main__":
    main()
