from colorama import Fore, Back, Style

class EnvFileNotFound(BaseException):
    """Raised when the environment ('.env') file is not found within the working directory."""
    def __init__(self):
        super().__init__(f'.env file not found in application directory.')

class DatabaseNotFoundError(BaseException):
    """Raised when a database doesn't exist at the specified filepath."""
    def __init__(self, database_path):
        super().__init__(f'Database "{database_path}" does not exist.')

class DatabaseAlreadyExists(BaseException):
    """Raised when a database already exists at the specified filepath."""
    def __init__(self, database_path):
        super().__init__(f'Database "{database_path}" already exists.')

class TableNotFoundError(BaseException):
    """Raised when a table doesn't exist in database."""
    def __init__(self, table_name):
        super().__init__(f'Table "{table_name}" does not exist in this database.')

class ModelInstanceNotFoundError(BaseException):
    """Raised when a model doesn't exist in the table."""
    def __init__(self, model_id):
        super().__init__(f'Model with id = "{model_id}" does not exist.')

class RelationshipError(BaseException):
    """Raised when an error occurs during attachment or detachment between models."""
    def __init__(self, message):
        super().__init__(message)

class DuplicateModelInstance(BaseException):
    """Raised when more than one of the same model instance is added to a collection."""
    def __init__(self, message):
       super().__init__(message)