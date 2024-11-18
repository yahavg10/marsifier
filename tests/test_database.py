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

        mock_db1.delete.assert_called_once_with("value")
        mock_db2.delete.assert_called_once_with("value")

    def test_fetch_key_from_all_databases(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        mock_db1.fetch.return_value = "value1"
        mock_db2.fetch.return_value = "value2"
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        result = db.fetch("key_to_fetch")

        self.assertEqual(result, {"db1": "value1", "db2": "value2"})
        mock_db1.fetch.assert_called_once_with("key_to_fetch")
        mock_db2.fetch.assert_called_once_with("key_to_fetch")

    def test_write_to_specific_database(self):
        mock_db = MagicMock()
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db}

        db.write(database_name="db1", some_key="value")

        mock_db.write.assert_called_once_with(some_key="value")

    def test_write_database_not_found(self):
        db = DataBase("databases_dir")
        db.databases = {}

        with patch("src.database.database.logger") as mock_logger:
            db.write(database_name="nonexistent_db", some_key="value")
            mock_logger.exception.assert_called_once_with("Database 'nonexistent_db' not found.")

    def test_delete_key_from_specific_database(self):
        mock_db = MagicMock()
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db}

        db.delete(key="key_to_delete", database_name="db1")

        mock_db.delete.assert_called_once_with("key_to_delete")

    def test_exists_key_in_specific_database(self):
        mock_db = MagicMock()
        mock_db.exists.return_value = True
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db}

        result = db.exists(key="key_to_check", database_name="db1")

        self.assertTrue(result)
        mock_db.exists.assert_called_once_with("key_to_check")

    def test_exists_key_not_found_in_any_database(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        mock_db1.exists.return_value = False
        mock_db2.exists.return_value = False
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        result = db.exists(key="key_to_check")

        self.assertFalse(result)
        mock_db1.exists.assert_called_once_with("key_to_check")
        mock_db2.exists.assert_called_once_with("key_to_check")

    def test_exists_key_found_in_any_database(self):
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        mock_db1.exists.return_value = False
        mock_db2.exists.return_value = True
        db = DataBase("databases_dir")
        db.databases = {"db1": mock_db1, "db2": mock_db2}

        result = db.exists(key="key_to_check")

        self.assertTrue(result)
        mock_db1.exists.assert_called_once_with("key_to_check")
        mock_db2.exists.assert_called_once_with("key_to_check")

    def test_fetch_empty_databases(self):
        db = DataBase("databases_dir")
        db.databases = {}

        result = db.fetch("key_to_fetch")

        self.assertEqual(result, {})

    def test_delete_empty_databases(self):
        db = DataBase("databases_dir")
        db.databases = {}

        db.delete(key="key_to_delete")

        # No databases to delete from, so nothing should happen
        self.assertEqual(len(db.databases), 0)

    def test_write_empty_databases(self):
        db = DataBase("databases_dir")
        db.databases = {}

        db.write(some_key="value")

        # No databases to write to, so nothing should happen
        self.assertEqual(len(db.databases), 0)


if __name__ == "__main__":
    unittest.main()
