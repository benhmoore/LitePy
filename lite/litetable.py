import sqlite3, os
from colorama import Fore, Back, Style
from lite.liteexceptions import *
from lite.lite import Lite

import pkg_resources # Used to store the version of Lite used to create a database.

class LiteTable:

    def get_foreign_key_references(self):
        self.cursor.execute(f'PRAGMA foreign_key_list({self.table_name})')
        foreign_keys = self.cursor.fetchall()

        foreign_key_map = {}

        for fkey in foreign_keys:
            table_name = fkey[2]
            foreign_key = fkey[3]
            local_key = fkey[4]

            if table_name not in foreign_key_map: foreign_key_map[table_name] = []

            foreign_key_map[table_name].append([local_key, foreign_key])
            
        return foreign_key_map

    @staticmethod
    def exists(table_name=None):
        database_path = Lite.get_database_path()
        if os.path.exists(database_path):
            if table_name:
                try: 
                    tbl = LiteTable(table_name)
                except TableNotFoundError:
                    return False
                return True
            else:
                return True
        else:
            return False

    @staticmethod
    def is_pivot_table(table_name):
        temp_table = LiteTable(table_name)
        temp_table.cursor.execute(f'PRAGMA table_info({table_name})')

        table_columns = [column[1] for column in temp_table.cursor.fetchall()]
        table_columns.remove('id')

        if len(table_columns) != 2: return False

        total_relations = 0
        fkey_refs = temp_table.get_foreign_key_references()
        for fkey_ref in fkey_refs:
            for relation in fkey_refs[fkey_ref]:
                total_relations += 1

        if total_relations != 2: return False

        return True
                
    @staticmethod
    def create_database(database_path):
        """Creates an SQLite database.

        Args:
            database_path (str): The full path of the SQlite database to create
        """

        if not os.path.exists(database_path):  
            # If it doesn't, create it
            print(Fore.YELLOW,"Creating Lite database. Lite version:", pkg_resources.get_distribution("lite").version, Fore.RESET)
            open(database_path, 'a').close() # Create DB file

            # Create config table
            LiteTable.create_table('config', {
                "key": "TEXT NOT NULL UNIQUE",
                "value": "TEXT"
            }, 'id')

            configTable = LiteTable('config')
            configTable.insert({"key": "lite_version", "value": pkg_resources.get_distribution("lite").version})
        
        return True

    @staticmethod
    def create_table(table_name:str, columns:dict, primary_key:str="id", foreign_keys:dict={}):
        database_path = Lite.get_database_path()
        
        table_desc = []
        for column_name in columns:
            table_desc.append(f'"{column_name}"	{columns[column_name]}')

        if primary_key: table_desc.append(f'PRIMARY KEY("{primary_key}" AUTOINCREMENT)')

        for column_name in foreign_keys:
            table_desc.append(f'FOREIGN KEY("{column_name}") REFERENCES "{foreign_keys[column_name][0]}"("{foreign_keys[column_name][1]}")')

        table_desc_str = ",\n".join(table_desc)

        table_sql = f"""
            CREATE TABLE "{table_name}" (
                "id" INTEGER NOT NULL UNIQUE,
                {table_desc_str}
            );
        """

        temp_connection = sqlite3.connect(database_path)
        temp_cursor = temp_connection.cursor()
        temp_cursor.execute(table_sql)
        temp_connection.commit()

        return True

    @staticmethod
    def delete_table(table_name:str):
        database_path = Lite.get_database_path()
        temp_connection = sqlite3.connect(database_path)
        temp_cursor = temp_connection.cursor()

        temp_cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

        return True

    def get_all_table_names(self):
        """Returns a list of all tables in current database."""
        self.cursor.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name")
        names = [row[0] for row in self.cursor.fetchall()]
        return names;

        

    def execute_and_commit(self, sql_str:str, values=(),should_log=True):
        """Executes and commits an sql query. Logs query.

        Args:
            sql_str (str): SQLite-compatible query
            values (tuple, optional): _description_. Defaults to ().
        """

        self.cursor.execute(sql_str, values)
        self.connection.commit()

        if should_log:
            safe_values = []
            for value in values:
                safe_values.append(str(value)[:30])
            safe_values_str = ", ".join(safe_values)
                
            self.log.append([sql_str,safe_values])

            # insertTable = LiteTable('query_log')

            # insertTable.insert({
            #     "query": sql_str,
            #     "query_values": safe_values_str
            # },False,False)

    def insert(self, columns, or_ignore=False, should_log=True):
        columns_str = ", ".join([cname for cname in columns])
        values_str = ", ".join(["?" for cname in columns])
        values_list = [columns[cname] for cname in columns]

        insert_sql = f'INSERT {"OR IGNORE" if or_ignore else ""} INTO {self.table_name} ({columns_str}) VALUES({values_str})'
        self.execute_and_commit(insert_sql, tuple(values_list),should_log)

        return True

    def update(self, update_columns:dict, where_columns:list, or_ignore=False):
        """_summary_

        Where Column Format: ['column','= or LIKE','value']

        Args:
            update_columns (dict): _description_
            where_columns (list): _description_
            or_ignore (bool, optional): _description_. Defaults to False.
        """

        set_str = ",".join([f'{cname} = ?' for cname in update_columns])
        values_list = [update_columns[cname] for cname in update_columns] # collect update values
        where_str = ",".join([f'{column[0]} {column[1]} ?' for column in where_columns])

        values_list += [column[2] for column in where_columns] # add where values

        self.execute_and_commit(f'UPDATE {"OR IGNORE" if or_ignore else ""} {self.table_name} SET {set_str} WHERE {where_str}', tuple(values_list))

        return True

    def select(self, where_columns:list, result_columns:list=['*']):
        get_str = ",".join([cname for cname in result_columns])
        where_str = " AND ".join([f'{column[0]} {column[1]} ?' for column in where_columns])
        values_list = [column[2] for column in where_columns] # add where values

        sql_str = f'SELECT {get_str} FROM {self.table_name} WHERE {where_str}'

        if len(where_columns) < 1: sql_str = f'SELECT {get_str} FROM {self.table_name}'

        self.log.append(sql_str)

        self.cursor.execute(sql_str,tuple(values_list))
        return self.cursor.fetchall()

    def delete(self, where_columns:list):
        where_str = " AND ".join([f'{column[0]} {column[1]} ?' for column in where_columns])
        values_list = [column[2] for column in where_columns] # add where values

        sql_str = f'DELETE FROM {self.table_name} WHERE {where_str}'
        
        if len(where_columns) < 1: sql_str = f'DELETE FROM {self.table_name}'

        self.execute_and_commit(sql_str,tuple(values_list))

        return True

    def __init__(self, table_name):
        database_path = Lite.get_database_path()

        if not os.path.exists(database_path):
            raise DatabaseNotFoundError(database_path)
        
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

        # Check if config tables exist
        self.cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="config"')
        if len(self.cursor.fetchall()) < 1: # Table doesn't exist
            raise InvalidDatabaseError(database_path)

        # Check if table exists
        self.cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}"')
        if len(self.cursor.fetchall()) < 1: # Table doesn't exist
            raise TableNotFoundError(table_name)

        self.log = []
        self.database_path = database_path
        self.table_name = table_name
    
    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception: pass
