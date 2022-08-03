import psycopg2, sqlite3
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
            "username": self.username,
            "password": self.password
        }
        return connection_config.__str__()

    def __init__(self, connection_type:connectionType=connectionType.SQLITE, host:str=None, port:str=None, database:str=None, username:str=None, password:str=None):
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

        if connection_type == connectionType.SQLITE:
            self.connection = sqlite3.connect(database)
        elif connection_type == connectionType.POSTGRESQL:
            self.connection = psycopg2.connect(database=database, host=host, user=username, password=password, port=port)

        self.cursor = self.connection.cursor()




    


