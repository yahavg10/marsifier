import unittest
from unittest.mock import patch, MagicMock
from src.utils.function_utils import get_receivers


class TestGetReceivers(unittest.TestCase):

    @patch("src.utils.function_utils.import_dynamic_model")
    def test_get_receivers_with_valid_configuration(self, mock_import_dynamic_model):
        mock_handler_instance = MagicMock()
        mock_import_dynamic_model.return_value = MagicMock(return_value=mock_handler_instance)

        config = MagicMock()
        config.receivers = {
            "receiver1": {"path": {"path": "some.module"}, "conf": {"key": "value"}}
        }

        result = get_receivers(config)
        self.assertIn("receiver1", result)
        self.assertEqual(result["receiver1"], mock_handler_instance)

    @patch("src.utils.function_utils.import_dynamic_model")
    def test_get_receivers_with_empty_configuration(self, mock_import_dynamic_model):
        config = MagicMock()
        config.receivers = {}

        result = get_receivers(config)
        self.assertEqual(result, {})

    @patch("src.utils.function_utils.import_dynamic_model", side_effect=ModuleNotFoundError)
    def test_get_receivers_with_missing_module(self, mock_import_dynamic_model):
        config = MagicMock()
        config.receivers = {"receiver1": {"path": {"path": "invalid.module"}, "conf": {}}}

        with self.assertRaises(ModuleNotFoundError):
            get_receivers(config)


if __name__ == "__main__":
    unittest.main()
