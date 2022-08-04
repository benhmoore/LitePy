import psycopg2, sqlite3, os
from enum import Enum, IntEnum
from lite import *



class connectionType(Enum):
    SQLITE = 1
    POSTGRESQL = 2

class LiteConnection:

    def __str__(self):
        connection_config = {
            "type": self.connection_type,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "database_path": self.database_path,
        }
        return connection_config.__str__()

    def __init__(self, connection_type:connectionType=connectionType.SQLITE, host:str=None, port:str=None, database:str=None, username:str=None, password:str=None, database_path:str=None, isolation:bool=False, WAL:bool=True):
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.database = database
        self.database_path = database_path
        # self.username = username
        # self.password = password

        if connection_type == connectionType.SQLITE:

            # Raise an error if the database doesn't exist
            if not os.path.exists(database_path):
                raise DatabaseNotFoundError(database_path)

            # Enable/disable isolation
            if isolation:
                self.connection = sqlite3.connect(database_path)
            else:
                self.connection = sqlite3.connect(database_path,isolation_level=None)

            self.cursor = self.connection.cursor()

            # Set journal mode
            if WAL:
                self.cursor.execute('PRAGMA journal_mode=wal;');
            else:
                self.cursor.execute('PRAGMA journal_mode=delete;')

        elif connection_type == connectionType.POSTGRESQL:
            self.connection = psycopg2.connect(database=database, host=host, user=username, password=password, port=port)
            self.cursor = self.connection.cursor()




    


