from typing import Callable, Optional

from configurations.config_models.app_model import AppConfig


class IoCContainer:
    def __init__(self):
        self.services = {}

    def register(self, cls, fn_init: Optional[Callable] = None, **kwargs):
        if getattr(cls, "_is_service", False):
            service_name = cls.__name__
            if fn_init:
                self.services[service_name] = fn_init(**kwargs)
            else:
                self.services[service_name] = cls(**kwargs)  # Pass the configuration to the service's __init__
            print(f"Registered service: {service_name}")

    def get_service(self, service_name):
        return self.services.get(service_name)

    def get_services(self, *service_names):
        services = [self.get_service(name) for name in service_names]
        return [service for service in services if service is not None]

    def inject_dependencies(self, func):
        if getattr(func, '_is_inject', False):
            dependency_name = func._dependency_name
            return self.get_service(dependency_name)
        return None
