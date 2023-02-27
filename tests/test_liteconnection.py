import os
import glob
import sqlite3
import unittest
from tests import *

# Define the database path for the test database
TEST_DB_PATH = "test.sqlite"

class TestLiteConnection(unittest.TestCase):

    def setUp(self):
        # Create a new test database
        Lite.create_database(TEST_DB_PATH)
        self.conn = LiteConnection(LiteConnection.TYPE.SQLITE, database_path=TEST_DB_PATH)

    def tearDown(self):
        # Delete the test database
        self.conn.cursor.close()
        self.conn.connection.close()

        # remove test database
        for file_name in glob.glob("*.sqlite*"):
            os.remove(file_name)

    def test_sqlite_connection(self):
        # Test that the SQLite connection was created successfully
        self.assertIsInstance(self.conn.connection, sqlite3.Connection)
        self.assertIsInstance(self.conn.cursor, sqlite3.Cursor)

    def test_database_not_found_error(self):
        # Test that a DatabaseNotFoundError is raised if the database doesn't exist
        with self.assertRaises(DatabaseNotFoundError):
            LiteConnection(LiteConnection.TYPE.SQLITE, database_path="non_existent.db")

    def test_execute(self):
        # Test the execute() method
        create_table_sql = "CREATE TABLE test_table (id INTEGER, name TEXT)"
        insert_data_sql = "INSERT INTO test_table VALUES (?, ?)"
        select_data_sql = "SELECT * FROM test_table"
        values = (1, "John")

        self.conn.execute(create_table_sql).commit()
        self.conn.execute(insert_data_sql, values).commit()

        result = self.conn.execute(select_data_sql).fetchall()
        self.assertEqual(result, [(1, "John")])

        result = self.conn.execute(select_data_sql).fetchone()
        self.assertEqual(result, (1, "John"))

if __name__ == '__main__':
    unittest.main()
