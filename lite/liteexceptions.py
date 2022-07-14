from colorama import Fore, Back, Style

class EnvFileNotFound(BaseException):
    """Raised when the table doesn't exist in database"""
    def __init__(self):
        print(Fore.RED, f'.env file not found in application directory.', Fore.RESET)

class InvalidDatabaseError(BaseException):
    """Raised when the table doesn't exist in database"""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" is not a valid LiteDatabase.', Fore.RESET)

class DatabaseNotFoundError(BaseException):
    """Raised when the table doesn't exist in database"""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" does not exist.', Fore.RESET)

class DatabaseAlreadyExists(BaseException):
    """Raised when a database already exists."""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" already exists.', Fore.RESET)

class TableNotFoundError(BaseException):
    """Raised when the table doesn't exist in database"""
    def __init__(self, table_name):
        print(Fore.RED, f'Table "{table_name}" does not exist in this database.', Fore.RESET)

class ModelInstanceNotFoundError(BaseException):
    """Raised when the model doesn't exist in the table"""
    def __init__(self, model_id):
        print(Fore.RED, f'Model with id = "{model_id}" does not exist.', Fore.RESET)

class RelationshipError(BaseException):
    """Raised when an error occurs during attachment or detachment between models."""
    def __init__(self, message):
        print(Fore.RED, message, Fore.RESET)

class DuplicateModelInstance(BaseException):
    """Raised when an error occurs when more than one of the same model instance are added to a collection."""
    def __init__(self, message):
        print(Fore.RED, message, Fore.RESET)