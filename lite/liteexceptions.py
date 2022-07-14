from colorama import Fore, Back, Style

class EnvFileNotFound(BaseException):
    """Raised when the environment ('.env') file is not found within the working directory."""
    def __init__(self):
        print(Fore.RED, f'.env file not found in application directory.', Fore.RESET)

class InvalidDatabaseError(BaseException):
    """Raised when a database doesn't contain a 'config' table."""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" is not a valid LiteDatabase. Make sure a config table exists.', Fore.RESET)

class DatabaseNotFoundError(BaseException):
    """Raised when a database doesn't exist at the specified filepath."""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" does not exist.', Fore.RESET)

class DatabaseAlreadyExists(BaseException):
    """Raised when a database already exists at the specified filepath."""
    def __init__(self, database_path):
        print(Fore.RED, f'Database "{database_path}" already exists.', Fore.RESET)

class TableNotFoundError(BaseException):
    """Raised when a table doesn't exist in database."""
    def __init__(self, table_name):
        print(Fore.RED, f'Table "{table_name}" does not exist in this database.', Fore.RESET)

class ModelInstanceNotFoundError(BaseException):
    """Raised when a model doesn't exist in the table."""
    def __init__(self, model_id):
        print(Fore.RED, f'Model with id = "{model_id}" does not exist.', Fore.RESET)

class RelationshipError(BaseException):
    """Raised when an error occurs during attachment or detachment between models."""
    def __init__(self, message):
        print(Fore.RED, message, Fore.RESET)

class DuplicateModelInstance(BaseException):
    """Raised when more than one of the same model instance is added to a collection."""
    def __init__(self, message):
        print(Fore.RED, message, Fore.RESET)