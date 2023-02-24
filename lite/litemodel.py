"""Contains the LiteModel class definition"""
import re
import typing
from lite import Lite, LiteTable, LiteCollection, LiteConnection, DB, LiteQuery
from lite.liteexceptions import ModelInstanceNotFoundError, RelationshipError


class LiteModel:
    """Describes a distinct model for database storage and methods
    for operating upon it.

    Raises:
        TypeError: Comparison between incompatible types.
        ModelInstanceNotFoundError: Model does not exist in database.
        RelationshipError: Relationship does not match required status.
    """
    DEFAULT_CONNECTION = None  # Overridden by LiteModel.connect()
    CUSTOM_PIVOT_TABLES = {}  # Filled by calls to .pivots_with()
    PIVOT_TABLE_CACHE = {}  # Used by belongs_to_many()

    # Declare common class attributes
    id = None
    created = None
    updated = None

    def __str__(self):
        return self.to_dict().__str__()

    def __repr__(self):
        attributes = [getattr(self, key) for key in self.table_columns]
        return str(tuple(attributes))

    def __lt__(self, other):
        try:
            return getattr(self, 'id') < getattr(other, 'id')
        except Exception as exc:
            raise TypeError from exc

    def __eq__(self, other):
        base_classes = [b_c.__name__ for b_c in other.__class__.__bases__]
        if (
            'LiteModel' in base_classes
            and self.table.table_name == other.table.table_name
            and self.table_columns == other.table_columns
        ):
            return all(
                getattr(self, col) == getattr(other, col)
                for col in self.table_columns
            )
        return False

    def __get_table_name(self) -> str:
        """Returns the derived table name by getting the plural noun form of
        the LiteModel instance's name.

        Returns:
            str: Derived table name
        """

        return Lite.pluralize_noun(self.__class__.__name__.lower())

    def __has_column(self, column_name: str) -> bool:
        """Checks if LiteModel instance has a given field or column.

        Args:
            column_name (str): Field name to look for

        Returns:
            bool
        """

        return column_name in self.table_columns

    def get_foreign_key_from_model(self, model) -> str:
        """Derives name of foreign key within current instance
        that references passed-in model.

        This is used to get the `primary key` value of the parent or
        child to this model. For example, if a `User` belongs to an `Account`,
        calling this method on `User` and passing in `Account` would return
        the name of the foreign key column referencing
        the particular `Account` instance the current `User` belongs to.

        - Called by attach(), detach(), belongs_to(), has_one(), and has_many().

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            str: Name of foreign key column referencing `parent` model instance
        """

        # Get conventional foreign key name and table name
        # try:  # Passed model is actually an instance
        self_fkey = f'{model.__class__.__name__.lower()}_id'
        model_table_name = model.table_name

        # !! This try block doesn't appear to be necessary
        # except AttributeError:  # Passed model is a LiteModel class
        #     self_fkey = f'{model.__name__.lower()}_id'
        #     model_table_name = Lite.pluralize_noun(model.__name__.lower())

        # Check if this table has a custom foreign key column name
        if model_table_name in self._foreign_key_map:
            self_fkey = self._foreign_key_map[model_table_name][0][1]

        return self_fkey

    def __get_pivot_name(self, model) -> str:
        """Returns the pivot table between `self` and the given LiteModel
        instance or class, if it exists.

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            str: Name of pivot table
        """

        # Check CUSTOM_PIVOT_TABLES for custom pivot table names
        # that define relationships between these two models
        self_name = self.__class__.__name__
        try:
            model_name = model.__class__.__name__
            if model_name == 'type':
                raise AttributeError
        except AttributeError:
            model_name = getattr(model, '__name__')

        for pivot_table_name, values in self.CUSTOM_PIVOT_TABLES.items():
            # Check if this pivot table is between these two models
            if set(values[:2]) == {model_name, self_name}:
                lite_connection = values[2]
                return pivot_table_name, lite_connection

        # Otherwise, derive conventional naming scheme for pivot tables
        # This table must be stored in the database denoted by Lite's
        # DEFAULT CONNECTION

        #  !! Considering removing this functionality

        # model_names = [self.__class__.__name__.lower()]
        # try:
        #     model_name = getattr(model, '__name__').lower()
        # except AttributeError:
        #     model_name = model.__class__.__name__.lower()

        # model_names.append(model_name)

        # model_names = sorted(model_names)  # Make alphabetical
        # pivot_table_name = '_'.join(model_names)  # Join into string

        # # Check to see if table with this name exists
        # if LiteTable.is_pivot_table(pivot_table_name):
        #     return pivot_table_name, None  # If it does, return the table name

    def __clean_attachments(self):
        """Internal method. Cleans up any references to a model instance
        that's being deleted. Called by .delete()."""

        # foreign_keys = self.table.get_foreign_key_references()
        table_names = self.table.get_table_names()

        check_tables = {}

        for t_name in table_names:
            temp_table = LiteTable(t_name)

            temp_foreign_keys = temp_table.get_foreign_key_references()

            if self.table.table_name in temp_foreign_keys:
                check_tables[temp_table.table_name] = temp_foreign_keys[self.table.table_name]

        # for t_name in check_tables:
        #     # Get local and foreign keys
        #     key_maps = check_tables[t_name]
        #     for i in range(0, len(key_maps)):
        #         local_key = key_maps[i][0]
        #         foreign_key = key_maps[i][1]

        #         local_key_value = getattr(self, local_key)

        #         # Check if table is a pivot table, as detach procedure will be different
        #         temp_table = LiteTable(t_name)
        #         if LiteTable.is_pivot_table(t_name):
        #             temp_table.delete([[foreign_key,'=',local_key_value]])
        #         else:
        #             temp_table.update({foreign_key: None}, [[foreign_key,'=',local_key_value]])
        for t_name, key_maps in check_tables.items():
            for local_key, foreign_key in key_maps:
                local_key_value = getattr(self, local_key)
                temp_table = LiteTable(t_name)
                if LiteTable.is_pivot_table(t_name):
                    temp_table.delete([[foreign_key, '=', local_key_value]])
                else:
                    temp_table.update({foreign_key: None}, [[foreign_key, '=', local_key_value]])

    def find_path_iter(self, open_n: list, closed_n: list, to_model_inst):
        """Internal method. Step function for .find_path()."""

        if not open_n:
            return False

        current_node = open_n.pop()
        if current_node not in closed_n:
            closed_n.append(current_node)

        if current_node == to_model_inst:
            path = [current_node]
            while (temp := getattr(current_node, 'parent')):
                path.append(temp)
                current_node = temp

            return list(reversed(path))

        methods = current_node.get_relationship_methods()
        relationship_models = LiteCollection()

        for method in methods:
            result = getattr(current_node, method)()
            if result:
                relationship_models = relationship_models + result

        for model in relationship_models:
            setattr(model, 'parent', current_node)
            if model not in closed_n:
                open_n.insert(0, model)

        return False

    def get_relationship_methods(self) -> list:
        """Returns a list of method names that define model-model relationships.

        To ensure methods are correctly identified as relationship definitions,
        make sure to specify a return type of `LiteCollection` or `LiteModel` when
        defining them.

        Returns:
            list: List of method names as strings
        """

        # Find all public attributes of this class
        instance_variables = set(filter(lambda x: x.startswith('_') is False, dir(self)))

        # Find all public, *default* LiteModel attributes
        default_variables = set(filter(lambda x: x.startswith('_') is False, dir(LiteModel)))

        # Determine attributes unique to this particular class
        unique_variables = instance_variables - default_variables

        # Isolate methods from other unique attributes
        unique_methods = []
        for i_var in unique_variables:
            try:
                getattr(getattr(self, i_var), '__call__')
                unique_methods.append(i_var)
            except AttributeError:
                continue

        # These methods should contain any relationship definitions
        # (has_one, has_many, belongs_to_many, etc.)
        # To find these relationship definitions, look for methods that return
        # either a LiteCollection or a LiteModel:
        relationship_definitions = []
        for method in unique_methods:
            method_signature = typing.get_type_hints(getattr(self, method))

            # Make sure return type is specified by method,
            # and that it is a LiteCollection or LiteModel
            if "return" in method_signature and method_signature['return'] in [
                LiteCollection,
                LiteModel,
            ]:
                relationship_definitions.append(method)

        return relationship_definitions

    def __init__(
            self,
            _id: int = None,
            _table: LiteTable = None,
            _values: list = None,
            _lite_conn: LiteConnection = None
    ):
        """LiteModel initializer.
        Parameters are used by internal methods and should not be provided."""

        if not _lite_conn:
            if self.DEFAULT_CONNECTION is not None:
                _lite_conn = self.DEFAULT_CONNECTION
            else:
                _lite_conn = Lite.DEFAULT_CONNECTION

        # Derive table name from class name
        if not hasattr(self, 'table_name'):
            self.table_name = self.__get_table_name()

        # Load table if not passed
        self.table = _table or LiteTable(self.table_name, _lite_conn)

        # Generate dict map of foreign key references. Used by .get_foreign_key_from_model()
        self._foreign_key_map = self.table.get_foreign_key_references()

        # Load model instance from database if an id is provided
        if _id is not None:

            columns = self.table.get_column_names()

            if not _values:
                _values = self.table.select([['id', '=', _id]])

            # Add columns and values to python class instance as attributes
            for col in enumerate(columns):
                value = _values[0][col[0]]
                setattr(self, col[1], value)

            # Store list of all table column names. Used by .save()
            self.table_columns = columns

    @classmethod
    def find_or_fail(cls, _id: int):
        """Returns a LiteModel instance with id matching the passed value.
        Throws an exception if an instance isn't found.

        Args:
            id (int): Id of model instance within database table

        Raises:
            ModelInstanceNotFoundError: Model does not exist in database.

        Returns:
            LiteModel: LiteModel with matching id
        """

        if cls.DEFAULT_CONNECTION is not None:
            lite_connection = cls.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        table_name = Lite.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, 'table_name'):
            table_name = cls.table_name

        table = LiteTable(table_name, lite_connection)
        rows = table.select([['id', '=', _id]])

        if len(rows) > 0:
            return cls(id, table, rows, lite_connection)
        raise ModelInstanceNotFoundError(_id)

    @classmethod
    def find(cls, _id: int):
        """Returns a LiteModel instance with id matching the passed value or None.

        Args:
            id (int): Id of model instance within database table

        Returns:
            LiteModel: LiteModel with matching id or None
        """

        try:
            return cls.find_or_fail(_id)
        except ModelInstanceNotFoundError:
            return None

    @classmethod
    def all(cls) -> LiteCollection:
        """Returns a LiteCollection containing all instances of this model.

        Returns:
            LiteCollection: Collection of all model instances
        """

        if cls.DEFAULT_CONNECTION is not None:
            lite_connection = cls.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        table_name = Lite.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, 'table_name'):
            table_name = cls.table_name

        table = LiteTable(table_name, lite_connection)

        rows = table.select([], ['id'])
        collection = [cls.find_or_fail(row[0]) for row in rows]
        return LiteCollection(collection)

    @classmethod
    def where(cls, column_name:str) -> LiteCollection:
        """Returns a LiteCollection containing all model instances matching where_columns.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            LiteCollection: Collection of matching model instances
        """

        return LiteQuery(cls, column_name)

        table_name = Lite.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, 'table_name'):
            table_name = cls.table_name

        # table_name = cls.pluralize(cls, cls.__name__.lower())
        # if hasattr(cls, 'table_name'):
        #     table_name = cls.table_name

        # table = LiteTable(table_name, lite_connection)

        # rows = table.select(where_columns, ['id'])
        # collection = [cls.find_or_fail(row[0]) for row in rows]
        # return LiteCollection(collection)

    @classmethod
    def create(cls, column_values: dict):
        """Creates a new instance of a LiteModel and returns it.

        Args:
            column_values (dict): The initial values to be stored for this model instance.

        Returns:
            LiteModel: Created model instance.
        """

        if cls.DEFAULT_CONNECTION is not None:
            lite_connection = cls.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        table_name = Lite.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, 'table_name'):
            table_name = cls.table_name

        # Insert into table
        table = LiteTable(table_name, lite_connection)
        table.insert(column_values)

        # Get latest instance with this id
        if table.connection.connection_type == DB.SQLITE:
            sql_str = f"""
                SELECT id FROM {table_name} 
                WHERE {list(column_values.keys())[0]} = ? 
                ORDER BY id DESC
            """
        elif table.connection.connection_type == DB.POSTGRESQL:
            sql_str = f"""
                SELECT id FROM {table_name} 
                WHERE {list(column_values.keys())[0]} = %s 
                ORDER BY id DESC
            """

        ids = table.connection.execute(
            sql_str, (column_values[list(column_values.keys())[0]],)
        ).fetchall()

        # This check should never fail
        if len(ids) > 0:
            return cls.find_or_fail(ids[0][0])
        raise ModelInstanceNotFoundError(-1)

    @classmethod
    def create_many(cls, column_list: list) -> LiteCollection:
        """Creates many new instances of a LiteModel and returns them within a LiteCollection.

        Args:
            column_values (dict): The initial values to be stored for this model instance.

        Returns:
            LiteCollection: Created model instances.
        """

        model_list = [cls.create(column_set) for column_set in column_list]
        return LiteCollection(model_list)

    @classmethod
    def pivots_with(cls, other_model, table_name: str, lite_connection: LiteConnection = None):
        """Notifies Lite of a many-to-many relationship. 
        This is only required when a custom pivot table name is used.

        Args:
            other_model (LiteModel): The other model forming the many-to-many relationship.
            table_name (str): Name of the pivot table storing the relationships.
        """

        if not lite_connection and cls.DEFAULT_CONNECTION is not None:
            lite_connection = Lite.DEFAULT_CONNECTION

        self_name = cls.__name__
        other_name = other_model.__name__

        cls.CUSTOM_PIVOT_TABLES[table_name] = [self_name, other_name, lite_connection]

    @classmethod
    def accessed_through(cls, lite_connection: LiteConnection):
        """Declares the connection Lite should use for this model.

        Args:
            lite_connection (LiteConnection): 
                Connection pointed to the database in which this model is stored
        """
        cls.DEFAULT_CONNECTION = lite_connection

    def to_dict(self) -> dict:
        """Converts LiteModel instance into human-readable dict, 
        truncating string values if necessary.

        Returns:
            dict: LiteModel attributes as dictionary
        """
        print_dict = {}

        for column in self.table_columns:
            attribute = getattr(self, column)

            if isinstance(attribute, bytes):
                attribute = attribute.decode("utf-8")

            if isinstance(attribute, str) and len(attribute) > 50:
                attribute = f'{attribute[:50]}...'

            print_dict[column] = attribute

        return print_dict

    def attach(self, model_instance, self_fkey: str = None, model_fkey: str = None):
        """Defines a relationship between two model instances.

        Args:
            model_instance (LiteModel): Model instance to attach to self.

        Raises:
            RelationshipError: Relationship already exists.
        """

        try:
            pivot_table_name, lite_connection = self.__get_pivot_name(model_instance)
        except (RelationshipError, AttributeError, TypeError):
            pivot_table_name = False

        if pivot_table_name:  # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name, lite_connection)

            # Derive foreign keys from pivot table
            foreign_keys = pivot_table.get_foreign_key_references()

            # user should provide a self and model foreign keys if the pivot
            # table associates two rows from the *same* table
            if not self_fkey or not model_fkey:
                if (model_instance.table_name == self.table_name
                        and len(foreign_keys[self.table_name]) > 1):
                    model_fkey = foreign_keys[model_instance.table_name][1][1]
                else:
                    model_fkey = foreign_keys[model_instance.table_name][0][1]

                self_fkey = foreign_keys[self.table_name][0][1]
            # Make sure this relationship doesn't already exist
            relationships = pivot_table.select([
                [self_fkey, '=', self.id],
                [model_fkey, '=', model_instance.id]
            ])

            # Insert relationship into pivot table
            if len(relationships) == 0:
                pivot_table.insert({
                    self_fkey: self.id,
                    model_fkey: model_instance.id
                })
            else:
                raise RelationshipError("This relationship already exists.")

            return True

        # Is not a many-to-many relationship
        # Derive foreign keys
        self_fkey = model_instance.get_foreign_key_from_model(self)
        model_fkey = self.get_foreign_key_from_model(model_instance)

        # Determine which model instance contains the reference to the other,
        # and make sure a relationship doesn't already exist.
        if self.__has_column(model_fkey):  # self contains foreign key reference
            if getattr(self, model_fkey) is not None:
                raise RelationshipError(
                    """There is a pre-existing relationship. 
                    Remove it with .detach() before proceeding."""
                )

            setattr(self, model_fkey, model_instance.id)
            self.save()
        elif getattr(model_instance, self_fkey) is None:
            setattr(model_instance, self_fkey, self.id)
            model_instance.save()
        else:
            raise RelationshipError(
                "There is a pre-existing relationship. Remove it with .detach() before proceeding."
            )

        return True

    def attach_many(self, model_instances):
        """Defines relationships between the current model instance and many model instances.

        Args:
            model_instances (list, LiteCollection): Model instances to attach to self.

        Raises:
            RelationshipError: Relationship already exists.
        """

        for model_instance in model_instances:
            self.attach(model_instance)

    def detach(self, model_instance):
        """Removes a relationship between two model instances.

        Args:
            model_instance (LiteModel): Model instance to detach from self.

        Raises:
            RelationshipError: Relationship does not exist.
        """

        try:
            pivot_table_name, lite_connection = self.__get_pivot_name(model_instance)
        except (AttributeError, TypeError):
            pivot_table_name = False

        if pivot_table_name:  # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name, lite_connection)

            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            if (model_instance.table_name == self.table_name
                    and len(foreign_keys[self.table_name]) > 1):
                model_fkey = foreign_keys[model_instance.table_name][1][1]
            else:
                model_fkey = foreign_keys[model_instance.table_name][0][1]

            self_fkey = foreign_keys[self.table_name][0][1]
            # Make sure this relationship doesn't already exist
            pivot_table.delete([
                [self_fkey, '=', self.id],
                [model_fkey, '=', model_instance.id]
            ])

        else:  # Is not many-to-many relationship
            # Derive foreign keys
            self_fkey = model_instance.get_foreign_key_from_model(self)
            model_fkey = self.get_foreign_key_from_model(model_instance)

            # Determine which model instance contains the reference to the other
            if self.__has_column(model_fkey):
                if getattr(self, model_fkey) != model_instance.id:
                    raise RelationshipError("Relationship does not exist. Cannot detach.")
                setattr(self, model_fkey, None)
                self.save()
            elif getattr(model_instance, self_fkey) == self.id:
                setattr(model_instance, self_fkey, None)
                model_instance.save()
            else:
                raise RelationshipError("Relationship does not exist. Cannot detach.")

    def detach_many(self, model_instances):
        """Removes relationships between the current model instance and many model instances.

        Args:
            model_instances (list, LiteCollection): Model instances to detach from self.

        Raises:
            RelationshipError: Relationship does not exist.
        """

        for model_instance in model_instances:
            self.detach(model_instance)

    def delete(self):
        """Deletes the current model instance.

        Raises:
            ModelInstanceNotFoundError: Model does not exist in database.
        """

        if self.id is None:
            # Cannot delete a model instance that isn't saved in database
            raise ModelInstanceNotFoundError(self.id)

        # Remove any attachments that would otherwise stick around after deleting the model instance
        self.__clean_attachments()

        self.table.delete([
            ['id', '=', self.id]
        ])

        # Since the python object instance cannot be removed from memory manually,
        # set all attributes to None
        for column in self.table_columns:
            setattr(self, column, None)

    def save(self):
        """Saves any changes to model instance attributes."""

        update_columns = {
            column: getattr(self, column)
            for column in self.table_columns
            if column != 'id'
        }
        if self.id is None:  # Create model if no id is provided
            self.table.insert(update_columns)
        else:
            self.table.update(update_columns, [['id', '=', self.id]])

    def fresh(self):
        """Reloads the model's attributes from the database."""

        # Load model instance from database by primary key
        _values = self.table.select([['id', '=', self.id]])

        # Set attributes of Python class instance
        # for i in range(len(self.table_columns)):
        #     try:
        #         value = _values[0][i]
        #     except IndexError as _:
        #         value = None
        #     setattr(self, self.table_columns[i], value)

        for col in enumerate(self.table_columns):
            value = _values[0][col[0]]
            setattr(self, col[1], value)

    def belongs_to(self, model, foreign_key: str = None):
        """Defines the current model instance as a child of the passed model class.

        Args:
            model (LiteModel): Parent model class
            foreign_key (str, optional): Custom foreign key name. 
                Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteModel: Parent model instance
        """

        # Derive foreign key if not provided
        if not foreign_key:
            foreign_key = self.get_foreign_key_from_model(model)

        # Get database row ID of parent model
        parent_model_id = getattr(self, foreign_key)

        return model.find(parent_model_id)

    def belongs_to_many(self, model) -> LiteCollection:
        """Defines a many-to-many relationship between the current model instance and a model class.

        Args:
            model (LiteModel): Sibling model class

        Returns:
            LiteCollection: Sibling model instances
        """

        # Check to see if pivot table exists - - -
        # First, check pivot table cache for this model
        model_class_name = getattr(model, '__name__').lower()
        if model_class_name not in self.PIVOT_TABLE_CACHE:
            pivot_table_name, lite_connection = self.__get_pivot_name(model)
            pivot_table = LiteTable(pivot_table_name, lite_connection)

            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            self.PIVOT_TABLE_CACHE[model_class_name] = [foreign_keys, pivot_table]
        else:  # If the pivot table for this relationship is already in the cache, use it
            foreign_keys, pivot_table = self.PIVOT_TABLE_CACHE[model_class_name]

        model_instance = model()

        # Handles pivot tables that relate two of the same model
        if model_instance.table_name == self.table_name and len(foreign_keys[self.table_name]) > 1:
            self_fkey = [foreign_keys[self.table_name][0][1], foreign_keys[self.table_name][1][1]]
            model_fkey = [
                foreign_keys[model_instance.table_name][1][1],
                foreign_keys[model_instance.table_name][0][1]
            ]
        else:
            self_fkey = foreign_keys[self.table_name][0][1]
            model_fkey = foreign_keys[model_instance.table_name][0][1]

        # Assume relationship is many-to-many
        siblings_collection = []
        relationships = []

        if isinstance(self_fkey, list):
            select_queries = [
                f"""
                    SELECT {model_fkey[i]} 
                    FROM {pivot_table.table_name} 
                    WHERE {self_fkey[i]} = {self.id}
                """
                for i in range(len(self_fkey))
            ]
            relationships = pivot_table.connection.execute(
                    ' UNION '.join(select_queries)
                ).fetchall()
        else:
            relationships = pivot_table.connection.execute(f"""
                SELECT {model_fkey} 
                FROM {pivot_table.table_name} 
                WHERE {self_fkey} = {self.id}
            """).fetchall()

        for rel in relationships:
            try:
                sibling = model.find(rel[0])
            except ModelInstanceNotFoundError:
                continue
            siblings_collection.append(sibling)

        return LiteCollection(siblings_collection)

    def has_one(self, model, foreign_key: str = None):
        """Reverse of belongs_to. 
        Defines the current model instance as a parent of the passed model class.

        Args:
            model (LiteModel): Child model class
            foreign_key (str, optional): 
                Custom foreign key name. Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteModel: Child model instance
        """

        # Get table name of model
        if not hasattr(model, 'table_name'):
            model.table_name = Lite.pluralize_noun(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key:
            foreign_key = model_instance.get_foreign_key_from_model(self)

        child_table = LiteTable(model.table_name)
        child_ids = child_table.select([
            [foreign_key, '=', self.id]
        ], ['id'])

        return model.find(child_ids[0][0]) if len(child_ids) > 0 else None

    def has_many(self, model, foreign_key: str = None) -> LiteCollection:
        """Defines the current model instance as a parent of many of the passed model class.

        Args:
            model (LiteModel): Children model class
            foreign_key (str, optional): 
                Custom foreign key name. Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteCollection: Children model instances
        """

        # Get table name of model
        if not hasattr(model, 'table_name'):
            model.table_name = Lite.pluralize_noun(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key:
            foreign_key = model_instance.get_foreign_key_from_model(self)

        child_table = LiteTable(model.table_name, model.DEFAULT_CONNECTION)
        child_rows = child_table.select([
            [foreign_key, '=', self.id]
        ], ['id'])

        children_collection = [model.find(row[0]) for row in child_rows]
        return LiteCollection(children_collection)

    @deprecated(reason="This method will be removed in a future release.")
    def find_path(self, to_model_instance, max_depth: int = 100):
        """Attempts to find a path from the current model instance 
        to another using Bidirectional BFS.

        Args:
            to_model_instance (LiteModel): Model instance to navigate to
            max_depth (int, optional): Maximum depth to traverse. Defaults to 100.

        Returns:
            LiteCollection or bool: Either the path or False for failure
        """

        setattr(self, 'parent', None)
        setattr(to_model_instance, 'parent', None)

        open_nodes = [self]
        reversed_open_nodes = [to_model_instance]
        closed_nodes = []
        reversed_closed_nodes = []

        for _ in range(max_depth):
            path = self.find_path_iter(open_nodes, closed_nodes, to_model_instance)
            if path is not False:
                return LiteCollection(path)

            reversed_path = to_model_instance.find_path_iter(
                reversed_open_nodes,
                reversed_closed_nodes,
                self
            )
            if reversed_path is not False:
                return LiteCollection(reversed(reversed_path))

        return LiteCollection([])
