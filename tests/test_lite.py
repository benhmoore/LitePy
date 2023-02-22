import os
import unittest
from lite import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"

class TestLite(unittest.TestCase):

    def setUp(self):
        """Create a test database"""
        Lite.createDatabase(TEST_DB_PATH)

    def tearDown(self):
        """Remove the test database"""
        
        # remove test database
        os.remove(TEST_DB_PATH)

    # Test Lite.getEnv()
    def test_get_env(self):
        with open(".env", "w") as env_file:
            env_file.write("DB_DATABASE=test.sqlite")
        env = Lite.getEnv()
        self.assertIsInstance(env, dict)

    # Test Lite.getDatabasePath()
    def test_get_database_path(self):
        # Test case where database path is specified in environment variables
        os.environ["DB_DATABASE"] = "test.sqlite"
        self.assertEqual(Lite.getDatabasePath(), "test.sqlite")

        # Test case where database path is specified in .env file
        os.environ.pop("DB_DATABASE", None)
        with open(".env", "w") as env_file:
            env_file.write("DB_DATABASE=test.sqlite")
        self.assertEqual(Lite.getDatabasePath(), "test.sqlite")

        # Test case where database path is not specified
        with open(".env", "w") as env_file:
            env_file.write("")
        with self.assertRaises(DatabaseNotFoundError):
            Lite.getDatabasePath()

    # Test Lite.createDatabase()
    def test_create_database(self):
        self.assertTrue(os.path.exists(TEST_DB_PATH))
        with self.assertRaises(DatabaseAlreadyExists):
            Lite.createDatabase(TEST_DB_PATH)

    # Test Lite.connect()
    def test_connect(self):
        conn = LiteConnection(database_path=TEST_DB_PATH)
        Lite.connect(conn)
        self.assertEqual(Lite.DEFAULT_CONNECTION, conn)

    # Test Lite.declareConnection()
    def test_declare_connection(self):
        conn = LiteConnection(database_path=TEST_DB_PATH)
        Lite.declareConnection("test", conn)
        self.assertEqual(Lite.DATABASE_CONNECTIONS["test"], conn)
