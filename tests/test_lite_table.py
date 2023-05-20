import os
import glob
import unittest
from tests import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"


class TestLiteTable(unittest.TestCase):
    def setUp(self):
        Lite.create_database(TEST_DB_PATH)
        Lite.connect(LiteConnection(database_path=TEST_DB_PATH))

        # test creating a table
        table_name = "test_table"
        columns = {"name": "TEXT", "age": "INTEGER", "parent_id": "INTEGER"}
        foreign_keys = {"parent_id": ("parents", "id")}
        LiteTable.create_table(table_name, columns, foreign_keys)
        self.table = LiteTable(table_name)

    def tearDown(self):
        # test deleting the table
        LiteTable.delete_table(self.table.table_name)
        self.assertFalse(LiteTable.exists(self.table.table_name))

        # remove test database
        for file_name in glob.glob("*.sqlite*"):
            os.remove(file_name)

    def test_table_creation(self):
        self.assertTrue(LiteTable.exists(self.table.table_name))

    def test_is_pivot_table(self):
        self.assertFalse(self.table.is_pivot_table("test"))
        self.assertFalse(self.table.is_pivot_table("test_table"))

    def test_column_names(self):
        self.assertSetEqual(
            set(self.table.get_column_names()),
            {"created", "updated", "id", "name", "age", "parent_id"},
        )

    def test_insert_row(self):
        row = {"id": 1, "name": "John", "age": 25, "parent_id": None}
        self.table.insert(row)
        self.assertListEqual(
            self.table.select([], ["id", "name", "age", "parent_id"]),
            [(1, "John", 25, None)],
        )

    def test_update_row(self):
        self.table.insert({"id": 1, "name": "John", "age": 25, "parent_id": None})
        self.table.update({"age": 26}, [("id", "=", 1)])
        self.assertListEqual(
            self.table.select([], ["id", "name", "age", "parent_id"]),
            [(1, "John", 26, None)],
        )

    def test_delete_row(self):
        self.table.insert({"id": 1, "name": "John", "age": 25, "parent_id": None})
        self.table.delete([("id", "=", 1)])
        self.assertListEqual(self.table.select([]), [])

    def test_delete_all(self):
        self.table.insert({"id": 1, "name": "John", "age": 25, "parent_id": None})
        self.table.insert({"id": 2, "name": "John", "age": 25, "parent_id": None})
        self.table.insert({"id": 3, "name": "John", "age": 25, "parent_id": None})
        self.table.delete()
        self.assertListEqual(self.table.select([]), [])


if __name__ == "__main__":
    unittest.main(exit=False)
    os.remove(TEST_DB_PATH)
