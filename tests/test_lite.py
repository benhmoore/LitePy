import os
import glob
import unittest
from tests import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"


class TestLite(unittest.TestCase):
    def setUp(self):
        """Create a test database"""
        Lite.create_database(TEST_DB_PATH)

    def tearDown(self):
        """Remove the test database"""

        # remove test database
        for file_name in glob.glob("*.sqlite*"):
            os.remove(file_name)

    # Test Lite.get_env()
    def test_get_env(self):
        os.remove(".env")
        with self.assertRaises(EnvFileNotFound):
            env = Lite.get_env()
        with open(".env", "w") as env_file:
            env_file.write("DB_DATABASE=test.sqlite")
        env = Lite.get_env()

        self.assertIsInstance(env, dict)
        self.assertEqual(env, {"DB_DATABASE": "test.sqlite"})

        os.remove(".env")

    # Test Lite.get_database_path()
    def test_get_database_path(self):
        # Test case where database path is specified in environment variables
        os.environ["DB_DATABASE"] = "test.sqlite"
        self.assertEqual(Lite.get_database_path(), "test.sqlite")

        # Test case where database path is specified in .env file
        os.environ.pop("DB_DATABASE", None)
        with open(".env", "w") as env_file:
            env_file.write("DB_DATABASE=test.sqlite")
        self.assertEqual(Lite.get_database_path(), "test.sqlite")

        # Test case where database path is not specified
        with open(".env", "w") as env_file:
            env_file.write("")
        with self.assertRaises(DatabaseNotFoundError):
            Lite.get_database_path()

    # Test Lite.create_database()
    def test_create_database(self):
        self.assertTrue(os.path.exists(TEST_DB_PATH))
        with self.assertRaises(DatabaseAlreadyExists):
            Lite.create_database(TEST_DB_PATH)

    # Test Lite.connect()
    def test_connect(self):
        conn = LiteConnection(database_path=TEST_DB_PATH)
        Lite.connect(conn)
        self.assertEqual(Lite.DEFAULT_CONNECTION, conn)

    # Test Lite.disconnect()
    def test_disconnect(self):
        conn = LiteConnection(database_path=TEST_DB_PATH)
        Lite.connect(conn)
        Lite.disconnect()
        self.assertEqual(Lite.DEFAULT_CONNECTION, None)

    # Test Lite.declare_connection()
    def test_declare_connection(self):
        conn = LiteConnection(database_path=TEST_DB_PATH)
        Lite.declare_connection("test", conn)
        self.assertEqual(Lite.DATABASE_CONNECTIONS["test"], conn)

    # Test Lite.HelperFunctions.pluralize_noun()
    def test_pluralize_noun(self):
        assert Lite.HelperFunctions.pluralize_noun("peach") == "peaches"
        assert Lite.HelperFunctions.pluralize_noun("class") == "classes"
        assert Lite.HelperFunctions.pluralize_noun("toy") == "toys"
        assert Lite.HelperFunctions.pluralize_noun("city") == "cities"
