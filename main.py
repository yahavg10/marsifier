from configurations.developer_config import app_config
from src.container import IoCContainer
from src.utils.file_utils import setup_logger

container = IoCContainer(app_config)
container.configure()


def main():
    setup_logger()
    container.database.setup_all_databases(app_config.databases["types"])
    container.database.write(key=container.pipeline.run_pipeline("C:/Users/nadav/Desktop/all_images/image12_a.jpg"),
                             expiry=60,
                             value="test")


if __name__ == "__main__":
    main()
