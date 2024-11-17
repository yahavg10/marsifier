import unittest
from unittest.mock import patch, MagicMock

from src.pipeline_runner.pipeline_utils import delete_all_united_files, get_valid_files


class TestUtilityFunctions(unittest.TestCase):

    @patch("src.utils.file_utils.os.path.exists")
    @patch("src.utils.file_utils.os.remove")
    def test_delete_all_united_files(self, mock_remove, mock_exists):
        mock_exists.side_effect = [True, False]
        mock_app_config = MagicMock()
        mock_app_config.sender["file_invoker"]["params"]["suffixes"] = [".txt", ".csv"]
        mock_app_config.receivers["file"]["conf"]["folder_to_monitor"] = "/some/path"

        delete_all_united_files("common_name", mock_app_config)

        mock_remove.assert_called_once_with("/some/path/common_name.txt")

    @patch("src.utils.file_utils.os.listdir")
    @patch("src.utils.file_utils.os.path.isfile")
    def test_get_valid_files(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ["file1.txt", "file2.csv", "not_a_file"]
        mock_isfile.side_effect = [True, True, False]

        valid_files = get_valid_files("/some/path")

        self.assertEqual(valid_files, ["file1.txt", "file2.csv"])


if __name__ == "__main__":
    unittest.main()
