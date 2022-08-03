from multiprocessing.sharedctypes import Value
import sqlite3, os
from lite import *

class LiteTable:
    """Facilitates common table operations on an SQLite database.

    Raises:
        DatabaseAlreadyExists: Database already exists at filepath
        DatabaseNotFoundError: Database not specified by environment file or variables.
        TableNotFoundError: Table not found within database
    """

    def getForeignKeyReferences(self) -> dict:
        """Returns dictionary of foreign keys associated with table.

        Returns:
            dict: {
                table_name: [
                    [local_key, foreign key]
                ]
            }
        """

        # Get raw list of foreign key relationships using 'PRAGMA'
        foreign_keys = self.executeAndFetch(f'PRAGMA foreign_key_list({self.table_name})')

        foreign_key_map = {
            # table_name: [local_key, foreign_key]
        }

        # Generate key mapping
        for fkey in foreign_keys:
            table_name = fkey[2]
            foreign_key = fkey[3]
            local_key = fkey[4]

            if table_name not in foreign_key_map: foreign_key_map[table_name] = []
            foreign_key_map[table_name].append([local_key, foreign_key])
            
        return foreign_key_map


    @staticmethod
    def exists(table_name:str) -> bool:
        """Checks if table exists in database.

        Args:
            table_name (str): Table name

        Returns:
            bool
        """

        database_path = Lite.getDatabasePath()
        if os.path.exists(database_path):
            try: tbl = LiteTable(table_name)
            except TableNotFoundError: return False
            return True
        else:
            return False


    @staticmethod
    def isPivotTable(table_name:str) -> bool:
        """Checks if table is pivot table by counting table columns and checking foreign key references.

        Args:
            table_name (str): Table name

        Returns:
            bool
        """

        # Ensure table exists
        try: temp_table = LiteTable(table_name)
        except: return False

        # Check that number of columns in table is equal to 2, not including 'id' field
        temp_table.cursor.execute(f'PRAGMA table_info({table_name})')

        table_columns = [column[1] for column in temp_table.cursor.fetchall()]
        table_columns.remove('id')

        if len(table_columns) != 2: return False

        # Check that number of foreign key relations is equal to 2
        total_relations = 0
        fkey_refs = temp_table.getForeignKeyReferences()
        for fkey_ref in fkey_refs:
            for relation in fkey_refs[fkey_ref]:
                total_relations += 1
        if total_relations != 2: return False

        return True


    @staticmethod
    def createTable(table_name:str, columns:dict, foreign_keys:dict={}):
        """Creates a table within the database.

        Args:
            table_name (str): Table name
            columns (dict): {
                column_name: field_attributes
            }
            foreign_keys (dict, optional): {
                column_name: [foreign_table_name, foreign_column_name]
            }
        """
        
        table_desc = [] # list of lines that will be combined to create SQL query string

        # Convert columns dict into lines for SQL query
        for column_name in columns:
            table_desc.append(f'"{column_name}"	{columns[column_name]}')

        # Declare primary key
        table_desc.append(f'PRIMARY KEY("id" AUTOINCREMENT)')

        # Declare foreign key relationships
        for column_name in foreign_keys:
            table_desc.append(f'FOREIGN KEY("{column_name}") REFERENCES "{foreign_keys[column_name][0]}"("{foreign_keys[column_name][1]}")')

        # Combine list of lines into newline-separated string, and generate complete sql query string
        table_desc_str = ",\n".join(table_desc) 
        table_sql = f"""
            CREATE TABLE "{table_name}" (
                "id" INTEGER NOT NULL UNIQUE,
                {table_desc_str}
            );
        """

        # Create table within database
        database_path = Lite.getDatabasePath() # Get database path from environment
        temp_connection = sqlite3.connect(database_path)
        temp_cursor = temp_connection.cursor()
        temp_cursor.execute(table_sql)
        temp_connection.commit()

        return LiteTable(table_name)


    @staticmethod
    def deleteTable(table_name:str):
        """Deletes a given table.

        Args:
            table_name (str): Table name
        """

        database_path = Lite.getDatabasePath()
        temp_connection = sqlite3.connect(database_path)
        temp_cursor = temp_connection.cursor()

        temp_cursor.execute(f'DROP TABLE IF EXISTS {table_name}')


    def getAllTableNames(self) -> list:
        """Returns a list of all tables in database.

        Returns:
            list: [table_name,..]
        """

        rows = self.executeAndFetch("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name")
        names = [row[0] for row in rows]
        return names

    
    def executeAndFetch(self, sql_str:str, values=()) -> list:
        """Executes and fetches an sql query.

        Args:
            sql_str (str): SQLite query
            values (tuple, optional): Any parameters to be passed to SQLite's .execute() method. Defaults to ().

        Returns:
            list: List of query results
        """

        self.cursor.execute(sql_str, values)
        results = self.cursor.fetchall()

        return results


    def executeAndCommit(self, sql_str:str, values=()):
        """Executes and commits an sql query.

        Args:
            sql_str (str): SQLite-compatible query
            values (tuple, optional): Any parameters to be passed to SQLite's .execute() method. Defaults to ().
        """

        self.cursor.execute(sql_str, values)
        self.connection.commit()


    def insert(self, columns, or_ignore=False):
        """Inserts row into database table.

        Args:
            columns (dict): {
                column_name: row_value
            }
            or_ignore (bool, optional): Ignore if row already exists. Defaults to False.
        """

        # Refactor pythonic variables into SQLite query string
        columns_str = ", ".join([cname for cname in columns])
        values_str = ", ".join(["?" for cname in columns])
        values_list = [columns[cname] for cname in columns]

        insert_sql = f'INSERT {"OR IGNORE" if or_ignore else ""} INTO {self.table_name} ({columns_str}) VALUES({values_str})'
        self.executeAndCommit(insert_sql, tuple(values_list))


    def update(self, update_columns:dict, where_columns:list, or_ignore=False):
        """Updates a row in database table.

        Args:
            update_columns (dict): {
                column_name: updated_row_value
            }
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]
            or_ignore (bool, optional): Ignore if row already exists. Defaults to False.
        """

        # Refactor pythonic variables into SQLite query string
        set_str = ",".join([f'{cname} = ?' for cname in update_columns])
        values_list = [update_columns[cname] for cname in update_columns] # collect update values
        where_str, where_values = self.__where_to_str(where_columns)

        values_list += where_values

        self.executeAndCommit(f'UPDATE {"OR IGNORE" if or_ignore else ""} {self.table_name} SET {set_str} WHERE {where_str}', tuple(values_list))


    def select(self, where_columns:list, result_columns:list=['*']) -> list:
        """Executes a select statement on database table.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]
            result_columns (list, optional): List of columns to include in results. Defaults to all.

        Returns:
            list: Query results
        """

        # Refactor pythonic variables into SQLite query string
        get_str = ",".join([cname for cname in result_columns])
        where_str, values_list = self.__where_to_str(where_columns)
        sql_str = f'SELECT {get_str} FROM {self.table_name} WHERE {where_str}'
        
        if len(where_columns) < 1: sql_str = f'SELECT {get_str} FROM {self.table_name}'

        return self.executeAndFetch(sql_str,tuple(values_list))


    def delete(self, where_columns:list):
        """Deletes rows from a database table. If where_columns is an empty list, deletes all rows.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]
        """

        where_str, values_list = self.__where_to_str(where_columns)

        sql_str = f'DELETE FROM {self.table_name} WHERE {where_str}'
        
        # Delete all rows if no where conditions provided
        if len(where_columns) < 1: sql_str = f'DELETE FROM {self.table_name}'

        self.executeAndCommit(sql_str,tuple(values_list))


    def __where_to_str(self, where_columns:list) -> tuple:
        """Internal method. Converts where_columns dict to a proper SQL query substring.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            tuple: (sql_substr <str>, values <list>)
        """

        where_str = " AND ".join([f'{column[0]} {column[1]} ?' for column in where_columns])
        values_list = [column[2] for column in where_columns] # add where values

        # Convert Python's None to NULL for the SQL query
        values_to_remove = []
        insert_positions = self.__find_char_occurrences(where_str, '?')
        where_str = list(where_str)

        remove_values = []
        for i in range(0, len(values_list)):
            if values_list[i] == None:
                del where_str[insert_positions[i]]
                where_str.insert(insert_positions[i], 'NULL')
                remove_values.append(i)
        
        for i in remove_values:
            del values_list[i]

        new_where_str = ''
        for i in where_str:
            new_where_str += i

        return (new_where_str, values_list)
        
        
    def __find_char_occurrences(self, str:str, char:str) -> list:
        """Internal method. Returns a list of indices where a character appears within string.

        Args:
            str (str): String to search within
            char (str): Character to look for

        Returns:
            list: List of occurrence indices
        """

        return [i for i, letter in enumerate(str) if letter == char]


    def __init__(self, table_name:str, disable_isolation=False, disable_WAL=False):
        """LiteTable initializer.

        Args:
            table_name (str): Name of table within database to connect to
            disable_isolation (bool, optional). Determines whether the SQLite connection disables isolation. Defaults to False.
            disable_WAL (bool, optional): Determines whether the SQLite connection disables WAL. Defaults to False.

        Raises:
            DatabaseNotFoundError: Database not found
            InvalidDatabaseError: Database isn't a valid Lite database
            TableNotFoundError: Table not found within database
        """

        database_path = Lite.getDatabasePath()

        # Raise an error if the database already exists
        if not os.path.exists(database_path):
            raise DatabaseNotFoundError(database_path)

        # Set isolation level
        if not disable_isolation:
            self.connection = sqlite3.connect(database_path,isolation_level=None)
        else:
            self.connection = sqlite3.connect(database_path)
            
        self.cursor = self.connection.cursor()

        # Set journal_mode
        if not disable_WAL:
            self.cursor.execute('PRAGMA journal_mode=wal;');
        else:
            self.cursor.execute('PRAGMA journal_mode=delete;')

        # Check if table with provided name exists
        if len(self.executeAndFetch(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}"')) < 1: # Table doesn't exist
            raise TableNotFoundError(table_name)

        # Store database and table attributes for later use
        self.database_path = database_path
        self.table_name = table_name


    def __del__(self):
        """Cleans up LiteTable instance by closing SQLite cursor and connection."""

        try:
            self.cursor.close()
            self.connection.close()
        except Exception: pass
