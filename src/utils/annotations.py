def Service(cls):
    """Decorator to mark a class as a service for automatic IoC registration."""
    cls._is_service = True
    return cls


def Inject(dependency_name):
    """Decorator to mark dependencies for injection."""

    def decorator(func):
        func._is_inject = True
        func._dependency_name = dependency_name
        return func

    return decorator


def Observer(subject_name):
    """Decorator to mark a class as an observer for a specific subject."""

    def decorator(cls):
        cls._is_observer = True
        cls._subject_name = subject_name
        return cls

    return decorator
