def Service(cls):
    cls._is_service = True
    return cls


def Inject(dependency_name):
    def decorator(func):
        func._is_inject = True
        func._dependency_name = dependency_name
        return func

    return decorator
