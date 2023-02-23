""" Contains the LiteTable class """
from lite import Lite, LiteConnection, DB
from lite.liteexceptions import TableNotFoundError


class LiteTable:
    """Facilitates common table operations on an SQLite database.

    Raises:
        DatabaseAlreadyExists: Database already exists at filepath
        DatabaseNotFoundError: Database not specified by environment file or variables.
        TableNotFoundError: Table not found within database
    """

    # PostgreSQL Support: ✅
    def get_foreign_key_references(self) -> dict:
        """Returns dictionary of foreign keys associated with table.

        Returns:
            dict: {
                table_name: [
                    [local_key, foreign key]
                ]
            }
        """

        # Get raw list of foreign key relationships using 'PRAGMA'
        if self.connection.connection_type == DB.SQLITE:
            foreign_keys = self.connection.execute(
                f"PRAGMA foreign_key_list({self.table_name})"
            ).fetchall()
        elif self.connection.connection_type == DB.POSTGRESQL:
            foreign_keys = self.connection.execute(f"""
                SELECT pg_get_constraintdef(oid) 
                FROM pg_constraint 
                WHERE conrelid='{self.table_name}'::regclass
            """).fetchall()

        _foreign_key_map = {
            # table_name: [local_key, foreign_key]
        }

        # Generate key mapping
        for fkey in foreign_keys:
            # Generate key mapping
            if self.connection.connection_type == DB.SQLITE:
                table_name = fkey[2]
                foreign_key = fkey[3]
                local_key = fkey[4]

                if table_name not in _foreign_key_map:
                    _foreign_key_map[table_name] = []
                _foreign_key_map[table_name].append([local_key, foreign_key])

            elif self.connection.connection_type == DB.POSTGRESQL:
                phrases = fkey[0].split('REFERENCES')
                if len(phrases) != 2:
                    continue

                foreign_key_phrase, local_key_phrase = phrases
                local_key = local_key_phrase[
                    local_key_phrase.find('(') + 1: local_key_phrase.find(')')
                ].strip()
                foreign_key = foreign_key_phrase[
                    foreign_key_phrase.find('(') + 1: foreign_key_phrase.find(')')
                ].strip()
                table_name = local_key_phrase.split('(')[0].strip()

                if table_name not in _foreign_key_map:
                    _foreign_key_map[table_name] = []
                _foreign_key_map[table_name].append([local_key, foreign_key])

        return _foreign_key_map

    # PostgreSQL Support: ✅
    @staticmethod
    def exists(table_name: str, lite_connection: LiteConnection = None) -> bool:
        """Checks if table exists in database.

        Args:
            table_name (str): Table name

        Returns:
            bool
        """

        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION

        try:
            LiteTable(table_name, lite_connection)
        except TableNotFoundError:
            return False
        return True

    # PostgreSQL Support: ✅
    @staticmethod
    def is_pivot_table(table_name: str, lite_connection: LiteConnection = None) -> bool:
        """Checks if table is pivot table by counting table columns 
        and checking foreign key references.

        Args:
            table_name (str): Table name

        Returns:
            bool
        """

        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION

        # Ensure table exists
        try:
            temp_table = LiteTable(table_name, lite_connection)
        except TableNotFoundError:
            return False

        # Check that number of columns in table is equal to 2, not including 'id' field
        table_columns = temp_table.get_column_names()

        table_columns.remove('id')
        table_columns.remove('created')
        table_columns.remove('updated')

        if len(table_columns) != 2:
            return False

        # Check that number of foreign key relations is equal to 2
        total_relations = 0
        fkey_refs = temp_table.get_foreign_key_references()
        for _, refs in fkey_refs.items():
            for _ in refs:
                total_relations += 1

        return total_relations == 2

    # PostgreSQL Support: ✅
    @staticmethod
    def create_table(
            table_name: str,
            columns: dict,
            foreign_keys: dict = None,
            lite_connection: LiteConnection = None
    ):
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
        if not foreign_keys:
            foreign_keys = {}
        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION

        table_desc = []  # list of lines that will be combined to create SQL query string

        # Create timestamp fields
        if lite_connection.connection_type == DB.SQLITE:
            table_desc.extend(
                (
                    '"created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    '"updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                )
            )
        # Declare primary key (PostgreSQL)
        if lite_connection.connection_type == DB.POSTGRESQL:
            table_desc.append('"id" serial primary key')

        # Convert columns dict into lines for SQL query
        table_desc.extend(
            f'"{column_name}"	{value}' for column_name, value in columns.items()
        )
        # Declare primary key (SQLite)
        if lite_connection.connection_type == DB.SQLITE:
            table_desc.extend(
                ('"id" INTEGER NOT NULL UNIQUE', 'PRIMARY KEY("id" AUTOINCREMENT)')
            )
        # Declare foreign key relationships
        table_desc.extend(
            f"""
                FOREIGN KEY("{column_name}") 
                REFERENCES "{value_[0]}" ("{foreign_keys[column_name][1]}")
            """
            for column_name, value_ in foreign_keys.items()
        )
        # Combine list of lines into newline-separated string,
        # and generate complete sql query string
        table_desc_str = ",\n".join(table_desc)

        table_sql = f"""
            CREATE TABLE "{table_name}" (
                {table_desc_str}
            );
        """

        # Create table within database
        lite_connection.execute(table_sql).commit()

        lite_connection.execute(f"""
            CREATE TRIGGER update_timestamp_{table_name} 
            AFTER UPDATE ON {table_name} 
            BEGIN UPDATE {table_name} 
            SET updated = CURRENT_TIMESTAMP 
            WHERE id = OLD.id; END;
        """).commit()

        return LiteTable(table_name, lite_connection)

    # PostgreSQL Support: ✅
    @staticmethod
    def delete_table(table_name: str, lite_connection: LiteConnection = None):
        """Deletes a given table.

        Args:
            table_name (str): Table name
        """

        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION

        if lite_connection.connection_type == DB.SQLITE:
            lite_connection.execute(f"DROP TABLE IF EXISTS {table_name}").commit()
        elif lite_connection.connection_type == DB.POSTGRESQL:
            lite_connection.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE").commit()

    # PostgreSQL Support: ✅
    @staticmethod
    def get_table_names(lite_connection: LiteConnection = None) -> list:
        """Returns a list of all tables in database.

        Returns:
            list: [table_name,..]
        """
        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION

        if lite_connection.connection_type == DB.SQLITE:
            rows = lite_connection.execute("""
                SELECT name FROM sqlite_schema 
                WHERE type='table' 
                ORDER BY name
            """).fetchall()
        elif lite_connection.connection_type == DB.POSTGRESQL:
            rows = lite_connection.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """).fetchall()

        return [row[0] for row in rows]

    # PostgreSQL Support: ✅
    def get_column_names(self) -> list:
        """Returns a list of the table's column names.

        Returns:
            list: Column names
        """

        if self.connection.connection_type == DB.SQLITE:
            table_columns = [column[1] for column in self.connection.execute(
                f'PRAGMA table_info({self.table_name})'
            ).fetchall()]
        elif self.connection.connection_type == DB.POSTGRESQL:
            table_columns = [column[0] for column in self.connection.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{self.table_name}'
            """).fetchall()]

        return table_columns

    # PostgreSQL Support: ✅
    def insert(self, columns, or_ignore=False):
        """Inserts row into database table.

        Args:
            columns (dict): {
                column_name: row_value
            }
            or_ignore (bool, optional): Ignore if row already exists. Defaults to False.
        """

        # Refactor pythonic variables into SQLite query string
        columns_str = ", ".join(list(columns))

        if self.connection.connection_type == DB.SQLITE:
            values_str = ", ".join(["?" for _ in columns])
        elif self.connection.connection_type == DB.POSTGRESQL:
            values_str = ", ".join(["%s" for _ in columns])
        values_list = [columns[cname] for cname in columns]

        insert_sql = f"""
            INSERT {'OR IGNORE' if or_ignore else ''} 
            INTO {self.table_name} ({columns_str})
            VALUES({values_str})
        """
        self.connection.execute(insert_sql, tuple(values_list)).commit()

    # PostgreSQL Support: ✅
    def update(self, update_columns: dict, where_columns: list, or_ignore: bool = False):
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
        if self.connection.connection_type == DB.SQLITE:
            set_str = ",".join([f'{cname} = ?' for cname in update_columns])
        elif self.connection.connection_type == DB.POSTGRESQL:
            set_str = ",".join([f'{cname} = %s' for cname in update_columns])
        values_list = [update_columns[cname] for cname in update_columns]  # collect update values
        where_str, where_values = self.__where_to_str(where_columns)

        values_list += where_values

        self.connection.execute(f"""
            UPDATE {'OR IGNORE' if or_ignore else ''} {self.table_name} 
            SET {set_str} 
            WHERE {where_str}
        """, tuple(values_list)).commit()

    # PostgreSQL Support: ✅
    def select(self, where_columns: list, result_columns: list = None) -> list:
        """Executes a select statement on database table.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]
            result_columns (list, optional): List of columns to include in results. Defaults to all.

        Returns:
            list: Query results
        """

        if not result_columns:
            result_columns = ['*']

        # Refactor pythonic variables into SQLite query string
        get_str = ",".join(list(result_columns))
        where_str, values_list = self.__where_to_str(where_columns)
        sql_str = f"SELECT {get_str} FROM {self.table_name} WHERE {where_str}"

        if not where_columns:
            sql_str = f"SELECT {get_str} FROM {self.table_name}"

        return self.connection.execute(sql_str, tuple(values_list)).fetchall()

    # PostgreSQL Support: ✅
    def delete(self, where_columns: list):
        """Deletes rows from a database table. If where_columns is an empty list, deletes all rows.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]
        """

        where_str, values_list = self.__where_to_str(where_columns)

        sql_str = f"DELETE FROM {self.table_name} WHERE {where_str}"

        # Delete all rows if no where conditions provided
        if not where_columns:
            sql_str = f"DELETE FROM {self.table_name}"

        self.connection.execute(sql_str, tuple(values_list)).commit()

    # PostgreSQL Support: ✅
    def __where_to_str(self, where_columns: list) -> tuple:
        """Internal method. Converts where_columns dict to a proper SQL query substring.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            tuple: (sql_substr <str>, values <list>)
        """

        where_str = " AND ".join([f'{column[0]} {column[1]} ?' for column in where_columns])
        values_list = [column[2] for column in where_columns]  # add where values

        # Convert Python's None to NULL for the SQL query
        insert_positions = self.__find_char_occurrences(where_str, '?')
        where_str = list(where_str)

        remove_values = []
        for i, value in enumerate(values_list):
            if value is None:
                del where_str[insert_positions[i]]
                where_str.insert(insert_positions[i], 'NULL')
                remove_values.append(i)

        for i in remove_values:
            del values_list[i]

        new_where_str = ''.join(where_str)
        # Convert '?' to '%s' when using PostgreSQL
        if self.connection.connection_type == DB.POSTGRESQL:
            new_where_str = new_where_str.replace('?', '%s')

        return (new_where_str, values_list)

    # PostgreSQL Support: ✅
    def __find_char_occurrences(self, _str: str, char: str) -> list:
        """Internal method. Returns a list of indices where a character appears within string.

        Args:
            str (str): String to search within
            char (str): Character to look for

        Returns:
            list: List of occurrence indices
        """

        return [i for i, letter in enumerate(_str) if letter == char]

    # PostgreSQL Support: ✅
    def __init__(self, table_name: str, lite_connection: LiteConnection = None):
        """LiteTable initializer.

        Args:
            table_name (str): Name of table within database to connect to
            disable_isolation (bool, optional): 
                Determines whether the SQLite connection disables isolation. Defaults to False.
            disable_WAL (bool, optional): 
                Determines whether the SQLite connection disables wal. Defaults to False.

        Raises:
            DatabaseNotFoundError: Database not found
            InvalidDatabaseError: Database isn't a valid Lite database
            TableNotFoundError: Table not found within database
        """

        if not lite_connection:
            lite_connection = Lite.DEFAULT_CONNECTION
        self.connection = lite_connection

        # Check if table with provided name exists
        if self.connection.connection_type == DB.SQLITE:
            if len(self.connection.execute(f"""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                AND name='{table_name}'
            """).fetchall()) < 1:  # Table doesn't exist
                raise TableNotFoundError(table_name)

        elif self.connection.connection_type == DB.POSTGRESQL:
            if len(self.connection.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public' 
                    AND table_type='BASE TABLE' 
                    AND table_name='{table_name}'
            """).fetchall()) < 1:
                raise TableNotFoundError(table_name)

        # Store database and table attributes for later use
        self.database_path = lite_connection.database_path
        self.table_name = table_name
