from colorama import Fore, Back, Style

import os
from lite import *

# class LiteConnection:
#     """Encapsulates a server connection for Lite.
#     """

#     def __init__():

class Lite:
    """Helper functions for other Lite classes.

    Raises:
        EnvFileNotFound: Environment ('.env') file not found in script directory
        DatabaseNotFoundError: Database not specified by environment file or variables.
    """

    @staticmethod
    def getEnv() -> dict:
        """Returns dict of values from .env file.

        Raises:
            EnvFileNotFound: Environment ('.env') file not found in script directory

        Returns:
            dict: Dictionary containing the key-value pairings from the .env file.
        """
        
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
    def getDatabasePath() -> str:
        """Returns sqlite database filepath.

        Raises:
            DatabaseNotFoundError: Database not specified by environment file or variables.

        Returns:
            str: Database filepath
        """

        db_path = os.environ.get('DB_DATABASE')
        if db_path is not None: # Look for database path in environment variables first
            return db_path
        else: # Otherwise, pull from .env file
            env = Lite.getEnv()
            if 'DB_DATABASE' in env:
                return env['DB_DATABASE']
            else:
                raise DatabaseNotFoundError('')