"""Contains the LiteConnection class and DB Enum"""
import os
import sqlite3
from pylite import DatabaseNotFoundError


class LiteConnection:
    """This class is used to create a connection to a database and execute queries."""

    def __init__(
        self, database_path: str = None, isolation: bool = False, wal: bool = True
    ) -> None:
        self.database_path = database_path

        # Raise an error if the database doesn't exist
        if not os.path.exists(database_path):
            raise DatabaseNotFoundError(database_path)
        elif database_path is None:
            raise DatabaseNotFoundError("No database path provided.")

        # Enable/disable isolation
        if isolation:
            self.connection = sqlite3.connect(database_path)
        else:
            self.connection = sqlite3.connect(database_path, isolation_level=None)

        self.cursor = self.connection.cursor()

        # Set journal mode
        self.cursor.execute(f"PRAGMA journal_mode={'wal' if wal else 'delete'};")

    class ExecuteResult:
        """An instance of this class is returned by a call to LiteConnection.execute().
        It includes modifier methods that can be stringed onto
        the .execute() call to commit or fetch.
        """

        def __init__(self, lite_connection: "LiteConnection") -> None:
            self.outer = lite_connection

        def commit(self) -> None:
            """Commits changes made by .execute() to the database."""

            self.outer.connection.commit()

        def fetchall(self) -> list[tuple[any, ...]]:
            """Makes a fetchall call to the database using the query passed to .execute()."""

            return self.outer.cursor.fetchall()

        def fetchone(self) -> tuple[any, ...]:
            """Makes a fetchone call to the database using the query passed to .execute()."""

            return self.outer.cursor.fetchone()

    def close(self) -> None:
        """Closes the connection to the database."""

        self.connection.close()

    def execute(self, sql_str: str, values: tuple[any, ...] = ()) -> ExecuteResult:
        """Executes a query on the database.

        Args:
            sql_str (str): the query to execute
            values (tuple, optional): the values to pass to the query. Defaults to ().

        Returns:
            ExecuteResult: an instance of the ExecuteResult class
        """

        self.cursor.execute(sql_str, values)
        return self.ExecuteResult(self)
