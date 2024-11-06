def Service(cls):
    cls._is_service = True
    return cls


def Inject(*dependency_names):
    def decorator(func):
        func._is_inject = True
        func._dependencies = dependency_names
        return func
    return decorator
