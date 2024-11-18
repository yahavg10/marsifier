import os
import unittest
from unittest.mock import patch, MagicMock
from src.utils.file_utils import load_configuration


class TestLoadConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["APP_CONFIG_PATH"] = "configurations/app.yml"

    @patch("builtins.open", new_callable=MagicMock)
    def test_load_configuration_file_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError("Config file not found")

        config_model = MagicMock()
        mock_load_conf_fn = MagicMock()

        with self.assertRaises(FileNotFoundError):
            load_configuration(config_model, mock_load_conf_fn)

    @patch("builtins.open", new_callable=MagicMock)
    def test_load_configuration_empty_file(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = ""

        config_model = MagicMock()
        mock_load_conf_fn = MagicMock(return_value={})  # No data parsed

        result = load_configuration(config_model, mock_load_conf_fn)
        self.assertEqual(result, config_model.from_dict.return_value)


if __name__ == "__main__":
    unittest.main()
