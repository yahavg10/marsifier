from src.container import IoCContainer

container = IoCContainer()

database_functions_template = ("get_instance_connection", "setup",
                               "connect", "disconnect",
                               "write", "fetch", "delete", "exists")

file_read_mode = "rb"

pipeline_steps = [
    {
        "name": "get_file_name"
    },
    {
        "name": "get_united_name",
    }
]
#     {
#         "name": "process_by_existence",
#         "config": {"folder_path": app_config.receivers["file"]["conf"]["folder_to_monitor"]}
#     }
