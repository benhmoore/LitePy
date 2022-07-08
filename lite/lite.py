import os
from lite.liteexceptions import EnvFileNotFound, DatabaseNotFoundError

class Lite:

    @staticmethod
    def command(self):
        print("HELLO")

    @staticmethod
    def get_env():
        env_dict = {}
        if os.path.exists('.env'):
            with open('.env') as env:
                for line in env:
                    key, value = line.split('=')
                    env_dict[key] = value
            return env_dict
        else:
            raise EnvFileNotFound()
    
    @staticmethod
    def get_database_path():
        db_path = os.environ.get('DB_DATABASE')
        if db_path is not None: # Look for database path in environment variables first
            return db_path
        else: # Otherwise, pull from .env file
            env = Lite.get_env()
            if 'DB_DATABASE' in env:
                return env['DB_DATABASE']
            else:
                raise DatabaseNotFoundError('')