import inspect
from functools import wraps
from typing import Callable, Optional


class IoCContainer:
    def __init__(self):
        self.services = {}

    def register(self, cls, fn_init: Optional[Callable] = None, **kwargs):
        if getattr(cls, "_is_service", False):
            service_name = cls.__name__

            service_instance = fn_init(**kwargs) if fn_init else cls(**kwargs)
            # Wrap methods with @Inject for dependency injection
            for attr_name in dir(service_instance):
                method = getattr(service_instance, attr_name)

                if callable(method) and getattr(method, '_is_inject', False):
                    wrapped_method = self._inject_dependencies(method)
                    setattr(service_instance, attr_name, wrapped_method)

            self.services[service_name] = service_instance

    def get_service(self, service_name):
        return self.services.get(service_name)

    def register_class(self, service_instance):
        for attr_name in dir(service_instance):
            method = getattr(service_instance, attr_name)

            if callable(method) and getattr(method, '_is_inject', False):
                wrapped_method = self._inject_dependencies(method)
                setattr(service_instance, attr_name, wrapped_method)
        self.services[service_instance.__class__.__name__] = service_instance

    def get_services(self, *service_names):
        services = [self.get_service(name) for name in service_names]
        return [service for service in services if service is not None]

    def _inject_dependencies(self, func):
        dependencies = func._dependencies

        @wraps(func)
        def wrapper(*args, **kwargs):
            injected_args = [self.get_service(dep) for dep in dependencies]
            return func(*injected_args, *args, **kwargs)

        return wrapper

    def register_functions_in_module(self, module):
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if hasattr(func, "_is_inject") and getattr(func, "_is_inject"):
                self.register_function(func)

    def register_function(self, func):
        if getattr(func, "_is_inject", False):
            wrapped_func = self._inject_dependencies(func)
            self.services[func.__name__] = wrapped_func
