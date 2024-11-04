from src.receiver.data_sources_handlers.file_handler import FileDataSourceHandler
from src.receiver.receiver import Receiver
from src.utils.function_utils import import_dynamic_model


class IoCContainer:
    def __init__(self, config):
        self.config = config
        self._services = {}

    def configure(self):
        self._services["receiver"] = Receiver(self.get_receivers())

    def get_receivers(self):
        receivers = {}
        for receiver_name, receiver_conf in self.config.receivers.items():
            receiver_model = import_dynamic_model(receiver_conf["path"])
            receivers[receiver_name] = receiver_model(**receiver_conf["conf"])
        return receivers

    def get_service(self, service_name):
        if service_name in self._services:
            return self._services[service_name]
        raise ValueError(f"Service '{service_name}' not registered")
