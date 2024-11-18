import unittest
from unittest.mock import patch, MagicMock

from src.receiver.data_sources_handlers.file_handler import FileDataSourceHandler
from src.utils.function_utils import import_dynamic_model


class TestImportDynamicModel(unittest.TestCase):
    @patch("importlib.import_module")
    def test_import_dynamic_model_module_not_found(self, mock_import_module):
        mock_import_module.side_effect = ModuleNotFoundError("Module not found")

        class_model_config = {"model_path": "nonexistent.module", "model_name": "SomeClass"}
        with self.assertRaises(ModuleNotFoundError):
            import_dynamic_model(class_model_config)

    @patch("importlib.import_module")
    def test_import_dynamic_model_invalid_model_path(self, mock_import_module):
        mock_import_module.side_effect = ValueError("Invalid path")

        class_model_config = {"model_path": None, "model_name": "SomeClass"}
        with self.assertRaises(ValueError):
            import_dynamic_model(class_model_config)

    def test_import_dynamic_model_success(self):
        class_model_config = {"model_path": "src.receiver.data_sources_handlers.file_handler", "model_name": "FileDataSourceHandler"}
        result = import_dynamic_model(class_model_config)

        self.assertEqual(result, FileDataSourceHandler)


if __name__ == "__main__":
    unittest.main()
