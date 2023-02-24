""" Contains the LiteConnection class and DB Enum """
try:
    import psycopg2
except ImportError:
    pass

import os
import sqlite3
from enum import Enum
from lite import DatabaseNotFoundError


class DB(Enum):
    """ Enum for database types """
    SQLITE = 1
    POSTGRESQL = 2


class LiteConnection:
    """This class is used to create a connection to a database and execute queries."""

    def __str__(self):
        connection_config = {
            "type": self.connection_type,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "database_path": self.database_path,
        }
        return connection_config.__str__()

    def __init__(
            self,
            connection_type: DB = DB.SQLITE,
            host: str = None,
            port: str = None,
            database: str = None,
            username: str = None,
            password: str = None,
            database_path: str = None,
            isolation: bool = False,
            wal: bool = True
    ):
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.database = database
        self.database_path = database_path

        if connection_type == DB.SQLITE:

            # Raise an error if the database doesn't exist
            if not os.path.exists(database_path):
                raise DatabaseNotFoundError(database_path)

            # Enable/disable isolation
            if isolation:
                self.connection = sqlite3.connect(database_path)
            else:
                self.connection = sqlite3.connect(database_path, isolation_level=None)

            self.cursor = self.connection.cursor()

            # Set journal mode
            if wal:
                self.cursor.execute('PRAGMA journal_mode=wal;')
            else:
                self.cursor.execute('PRAGMA journal_mode=delete;')

        elif connection_type == DB.POSTGRESQL:
            self.connection = psycopg2.connect(
                database=database,
                host=host,
                user=username,
                password=password,
                port=port
            )
            self.cursor = self.connection.cursor()

    class ExecuteResult:
        """
        An instance of this class is returned by a call to LiteDriver.execute().
        It includes modifier methods that can be stringed onto
        the .execute() call to commit or fetch.
        """

        def __init__(self, lite_driver):
            self.outer = lite_driver

        def commit(self) -> None:
            """Commits changes made by .execute() to the database."""
            self.outer.connection.commit()

        def fetchall(self) -> list:
            """Makes a fetchall call to the database using the query passed to .execute()."""
            return self.outer.cursor.fetchall()

        def fetchone(self):
            """Makes a fetchone call to the database using the query passed to .execute()."""
            return self.outer.cursor.fetchone()

    def execute(self, sql_str: str, values: tuple = ()):
        """Executes a query on the database."""

        print(sql_str)
        self.cursor.execute(sql_str, values)
        return self.ExecuteResult(self)
