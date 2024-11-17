import unittest
from unittest.mock import patch, MagicMock
from src.utils.function_utils import object_classes_getter


class TestObjectClassesGetter(unittest.TestCase):
    @patch("os.listdir")
    def test_object_classes_getter_no_python_files(self, mock_listdir):
        mock_listdir.return_value = ["textfile.txt", "README.md"]

        config = {"types": {}}
        directory = "src/handlers"

        result = object_classes_getter(config, directory)
        self.assertEqual(result, {})

    @patch("os.listdir")
    def test_object_classes_getter_empty_directory(self, mock_listdir):
        mock_listdir.return_value = []

        config = {"types": {}}
        directory = "src/handlers"

        result = object_classes_getter(config, directory)
        self.assertEqual(result, {})



if __name__ == "__main__":
    unittest.main()
