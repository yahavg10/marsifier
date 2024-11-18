import unittest
from unittest.mock import MagicMock

from src.container import IoCContainer
from src.utils.annotations import Inject


class MyService:
    def __init__(self):
        pass

    @Inject("dep1", "dep2")
    def process(self, dep1, dep2):
        return f"{dep1.do_something()} and {dep2.do_something()}"


class TestContainer(unittest.TestCase):

    def test_multiple_dependencies_injected(self):
        container = IoCContainer()

        mock_dep1 = MagicMock()
        mock_dep2 = MagicMock()
        mock_dep1.do_something.return_value = "Mock Dep1 Action"
        mock_dep2.do_something.return_value = "Mock Dep2 Action"

        container.register_class(mock_dep1)
        container.register_class(mock_dep2)

        my_service = MyService()
        container.register_class(my_service)

        retrieved_service = container.get_service(my_service.__class__.__name__)

        result = retrieved_service.process()

        assert result == "Mock Dep1 Action and Mock Dep2 Action"
        mock_dep1.do_something.assert_called_once()
        mock_dep2.do_something.assert_called_once()

    def test_method_with_multiple_injections(self):
        container = IoCContainer()

        mock_dep1 = MagicMock()
        mock_dep2 = MagicMock()
        mock_dep1.do_something.return_value = "Mock Dep1 Action"
        mock_dep2.do_something.return_value = "Mock Dep2 Action"

        container.register_class(mock_dep1)
        container.register_class(mock_dep2)

        mock_service = MagicMock()
        mock_service.perform_action.return_value = "Mock Dep1 Action and Mock Dep2 Action"

        container.register_class(mock_service)

        service = container.get_service("ServiceWithDependencies")

        result = service.perform_action(mock_dep1, mock_dep2)

        assert result == "Mock Dep1 Action and Mock Dep2 Action"
        mock_dep1.do_something.assert_called_once()
        mock_dep2.do_something.assert_called_once()

    def test_function_with_injected_dependencies(self):
        container = IoCContainer()

        mock_dep = MagicMock()
        mock_dep.do_something.return_value = "Mocked Function Dependency Action"

        container.register_class(mock_dep)

        def function_with_dep(dep):
            return dep.do_something()

        function_with_dep._is_inject = True

        container.register_function(function_with_dep)

        injected_function = container.get_service("function_with_dep")
        result = injected_function(mock_dep)

        assert result == "Mocked Function Dependency Action"
        mock_dep.do_something.assert_called_once()

    def test_circular_dependency(self):
        container = IoCContainer()

        mock_dep1 = MagicMock()
        mock_dep2 = MagicMock()

        mock_service_a = MagicMock()
        mock_service_a.action_a.return_value = "Mock Action A"

        mock_service_b = MagicMock()
        mock_service_b.action_b.return_value = "Mock Action B"

        container.register_class(mock_service_a)
        container.register_class(mock_service_b)

        assert mock_service_a.action_a() == "Mock Action A"
        assert mock_service_b.action_b() == "Mock Action B"

    def test_register_functions_in_module_with_multiple_functions(self):
        container = IoCContainer()

        mock_module = MagicMock()
        mock_module.func1._is_inject = True
        mock_module.func2._is_inject = True

        mock_module.func1.return_value = "Function 1 Result"
        mock_module.func2.return_value = "Function 2 Result"

        container.register_functions_in_module(mock_module)

        assert "func1" in container.services
        assert "func2" in container.services

        result1 = container.services["func1"]()
        result2 = container.services["func2"]()

        assert result1 == "Function 1 Result"
        assert result2 == "Function 2 Result"

    def test_lazy_loading_of_services(self):
        container = IoCContainer()

        mock_service = MagicMock()
        mock_service.get_value.return_value = "Mocked Value"

        container.register_class(mock_service)

        assert "MyLazyService" not in container.services

        service = container.get_service("MyLazyService")

        assert service.get_value() == "Mocked Value"
        assert "MyLazyService" in container.services

    def test_non_existent_service_retrieval(self):
        container = IoCContainer()

        service = container.get_service("NonExistentService")

        assert service is None
