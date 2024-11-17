import unittest
from unittest.mock import patch, MagicMock

from src.database.database import DataBase


class TestDataBase(unittest.TestCase):
    @patch("src.database.database.logger")
    def test_fetch_database_not_found(self, mock_logger):
        db = DataBase("databases_dir")
        db.databases = {}

        result = db.fetch("some_key", "nonexistent_db")

        self.assertIsNone(result)
        mock_logger.exception.assert_called_with("Database 'nonexistent_db' not found.")

    def test_write_all_databases(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        db.write(some_key="value")

        mock_db1.write.assert_called_once_with(some_key="value")
        mock_db2.write.assert_called_once_with(some_key="value")

    def test_delete_all_databases(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        db.delete(key="value")

        mock_db1.write.assert_called_once_with(some_key="value")
        mock_db2.write.assert_called_once_with(some_key="value")

    def test_fetch_all_databases(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        db.fetch(key="value")

        mock_db1.write.assert_called_once_with(some_key="value")
        mock_db2.write.assert_called_once_with(some_key="value")

if __name__ == "__main__":
    unittest.main()
