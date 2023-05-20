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
        self.conn = LiteConnection(database_path=TEST_DB_PATH)

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
            LiteConnection(database_path="non_existent.db")

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

    def test_connection_modes(self):
        # Create test databases
        isolation_wal_db = "isolation_wal.sqlite"
        isolation_db = "isolation.sqlite"
        wal_db = "wal.sqlite"
        Lite.create_database(isolation_wal_db)
        Lite.create_database(isolation_db)
        Lite.create_database(wal_db)

        # Test the isolation and wal modes
        self.conn = LiteConnection(database_path=isolation_wal_db, isolation=True)
        self.conn.execute("CREATE TABLE test_table (id INTEGER, name TEXT)").commit()
        self.conn.execute("INSERT INTO test_table VALUES (?, ?)", (1, "John")).commit()
        self.conn.execute("INSERT INTO test_table VALUES (?, ?)", (2, "Jane")).commit()
        self.conn.execute("INSERT INTO test_table VALUES (?, ?)", (3, "Jack")).commit()

        # Test isolation mode
        self.conn2 = LiteConnection(
            database_path=isolation_db, isolation=True, wal=False
        )
        self.conn2.execute("CREATE TABLE test_table (id INTEGER, name TEXT)").commit()
        result = self.conn2.execute("SELECT * FROM test_table").fetchall()
        self.assertEqual(result, [])

        # Test wal mode
        self.conn3 = LiteConnection(database_path=wal_db, isolation=False)
        self.conn3.execute("CREATE TABLE test_table (id INTEGER, name TEXT)").commit()
        self.conn3.execute("INSERT INTO test_table VALUES (?, ?)", (4, "Jill")).commit()
        result = self.conn3.execute("SELECT * FROM test_table").fetchall()
        self.assertEqual(result, [(4, "Jill")])

        # Close the connections
        self.conn.cursor.close()

        self.conn2.cursor.close()

        self.conn3.cursor.close()

        # Delete the test databases
        os.remove(isolation_wal_db)
        os.remove(isolation_db)
        os.remove(wal_db)


if __name__ == "__main__":
    unittest.main()
