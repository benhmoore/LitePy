import sqlite3, os
from colorama import Fore, Back, Style

class LiteServer:
    """A collection of SQLite helper functions
    """
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.log = []

    def execute_and_commit(self, sql_str:str, values=(),should_log=True):
        """Executes and commits an sql query. Logs query.

        Args:
            sql_str (str): SQLite-compatible query
            values (tuple, optional): _description_. Defaults to ().
        """

        print(sql_str)
        self.cursor.execute(sql_str, values)
        self.connection.commit()

        if should_log:
            safe_values = []
            for value in values:
                safe_values.append(str(value)[:30])
            safe_values_str = ", ".join(safe_values)
            print(safe_values_str)
                
            self.log.append([sql_str,safe_values])

            self.insert('query_log',{
                "query": sql_str,
                "query_values": safe_values_str
            },False,False)

    def create_database(self, database_path:str):
        """Creates an SQLite database.

        Args:
            database_path (str): The full path of the SQlite database to create
        """

        if not os.path.exists(database_path):  
            # If it doesn't, create it
            print(Fore.YELLOW,"Creating local application database...",Fore.RESET)
            open(database_path, 'a').close() # Create DB file

            # Connect to databse
            self.connect_to(database_path)

            # Create config table
            self.create_table('config', {
                "id": "INTEGER NOT NULL UNIQUE",
                "key": "TEXT NOT NULL UNIQUE",
                "value": "TEXT"
            }, 'id')

            # Create SQL log table
            self.create_table('query_log', {
                "id": "INTEGER NOT NULL UNIQUE",
                "query": "TEXT NOT NULL",
                "query_values": "TEXT"
            }, 'id')
        
    def connect_to(self, database_path:str):
        """Connects to an SQLite database.

        Args:
            database_path (str): The full path of the SQLite database to connect
        """

        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

    def create_table(self, table_name:str, columns:dict, primary_key:str, foreign_keys:dict={}):
        table_desc = []
        for column_name in columns:
            table_desc.append(f'"{column_name}"	{columns[column_name]}')

        if primary_key: table_desc.append(f'PRIMARY KEY("{primary_key}" AUTOINCREMENT)')

        for column_name in foreign_keys:
            table_desc.append(f'FOREIGN KEY("{column_name}") REFERENCES "{foreign_keys[column_name][0]}"("{foreign_keys[column_name][1]}")')

        table_desc_str = ",\n".join(table_desc)

        table_sql = f"""
            CREATE TABLE "{table_name}" (
                {table_desc_str}
            );
        """

        self.log.append([table_sql])
        self.cursor.execute(table_sql)
        self.connection.commit()

    def insert(self, table_name, columns, or_ignore=False, should_log=True):
        columns_str = ", ".join([cname for cname in columns])
        values_str = ", ".join(["?" for cname in columns])
        values_list = [columns[cname] for cname in columns]

        insert_sql = f'INSERT {"OR IGNORE" if or_ignore else ""} INTO {table_name} ({columns_str}) VALUES({values_str})'
        print(Fore.RED, insert_sql, tuple(values_list), Fore.RESET)
        self.execute_and_commit(insert_sql, tuple(values_list),should_log)

    def update(self, table_name, update_columns, where_columns, or_ignore=False):
        """_summary_

        Search Column format: ['column','= or LIKE','value']

        Args:
            table_name (_type_): _description_
            update_columns (_type_): _description_
            search_columns (_type_): _description_
        """

        set_str = ",".join([f'{cname} = ?' for cname in update_columns])
        values_list = [update_columns[cname] for cname in update_columns] # collect update values
        where_str = ",".join([f'{column[0]} {column[1]} ?' for column in where_columns])

        values_list += [column[2] for column in where_columns] # add where values

        self.execute_and_commit(f'UPDATE {"OR IGNORE" if or_ignore else ""} {table_name} SET {set_str} WHERE {where_str}', tuple(values_list))

    def select(self, table_name, where_columns, result_columns=['*']):
        get_str = ",".join([cname for cname in result_columns])
        where_str = ",".join([f'{column[0]} {column[1]} ?' for column in where_columns])
        values_list = [column[2] for column in where_columns] # add where values

        sql_str = f'SELECT {get_str} FROM {table_name} WHERE {where_str}'
        if len(where_columns) < 1: sql_str = f'SELECT {get_str} FROM {table_name}'

        self.log.append(sql_str)

        self.cursor.execute(sql_str,tuple(values_list))
        return self.cursor.fetchall()

    def delete(self, table_name, where_columns):
        pass

s = LiteServer()
# s.create_table(
#     'pages',
#     {
#         "id": "INTEGER NOT NULL UNIQUE",
#         "title": "TEXT NOT NULL",
#         "body": "TEXT NOT NULL",
#         "ref_id": "TEXT NOT NULL",
#     },
#     'id',
#     {
#         'ref_id':['references','id']
#     }
# )

s.create_database('test.db')
s.connect_to('test.db')
s.insert('config',{'key':'date_created','value':'never'},True)
s.update('config',{
    "value":22
},[
    ["key","=","date_created"]
])