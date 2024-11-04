from src.receiver.data_sources_handlers.data_source_handler_template import DataSourceHandlerTemplate


class FileDataSourceHandler(DataSourceHandlerTemplate):
    def __init__(self, file_path):
        self.file_path = file_path

    def fetch_data(self):
        print(f"Fetching data from file: {self.file_path}")
        return {"data": "sample file data"}
