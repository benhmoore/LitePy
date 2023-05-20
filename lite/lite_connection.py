"""Contains the LiteConnection class and DB Enum"""
import os
import sqlite3
from enum import Enum
from lite import DatabaseNotFoundError


class LiteConnection:
    """This class is used to create a connection to a database and execute queries."""

    class TYPE(Enum):
        """Enum for database types"""

        SQLITE = 1

    def __init__(
        self, database_path: str = None, isolation: bool = False, wal: bool = True
    ) -> None:
        self.connection_type = self.TYPE.SQLITE
        self.database_path = database_path

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
            self.cursor.execute("PRAGMA journal_mode=wal;")
        else:
            self.cursor.execute("PRAGMA journal_mode=delete;")

    class ExecuteResult:
        """An instance of this class is returned by a call to LiteDriver.execute().
        It includes modifier methods that can be stringed onto
        the .execute() call to commit or fetch.
        """

        def __init__(self, lite_driver) -> None:
            self.outer = lite_driver

        def commit(self) -> None:
            """Commits changes made by .execute() to the database."""

            self.outer.connection.commit()

        def fetchall(self) -> list[tuple]:
            """Makes a fetchall call to the database using the query passed to .execute()."""

            return self.outer.cursor.fetchall()

        def fetchone(self) -> tuple:
            """Makes a fetchone call to the database using the query passed to .execute()."""

            return self.outer.cursor.fetchone()

    def close(self) -> None:
        """Closes the connection to the database."""

        self.connection.close()

    def execute(self, sql_str: str, values: tuple = ()) -> ExecuteResult:
        """Executes a query on the database."""

        self.cursor.execute(sql_str, values)
        return self.ExecuteResult(self)
