"""Contains the LiteModel class definition"""
import typing
from lite import Lite, LiteTable, LiteCollection, LiteConnection, LiteQuery
from lite.lite_exceptions import ModelInstanceNotFoundError, RelationshipError


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
            return getattr(self, "id") < getattr(other, "id")
        except Exception as exc:
            raise TypeError from exc

    def __eq__(self, other):
        base_classes = [b_c.__name__ for b_c in other.__class__.__bases__]
        if (
            "LiteModel" in base_classes
            and self.table.table_name == other.table.table_name
            and self.table_columns == other.table_columns
        ):
            return all(
                getattr(self, col) == getattr(other, col) for col in self.table_columns
            )
        return False

    def _get_table_name(self) -> str:
        """Returns the derived table name by getting the plural noun form of
        the LiteModel instance's name.

        Returns:
            str: Derived table name
        """

        return Lite.HelperFunctions.pluralize_noun(self.__class__.__name__.lower())

    def get_foreign_key_column_for_model(self, model) -> str:
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

        # Check if this table has a custom foreign key column name
        if model.table_name in self._foreign_key_map:
            return self._foreign_key_map[model.table_name][0][1]

        # Get conventional foreign key name and table name
        return f"{model.__class__.__name__.lower()}_id"

    def _get_pivot_name(self, model) -> str:
        """Returns the pivot table between `self` and the given LiteModel
        instance or class, if it exists.

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            tuple: (pivot table name, lite_connection)
        """

        # Check CUSTOM_PIVOT_TABLES for custom pivot table names
        # that define relationships between these two models
        try:
            model_name = model.__class__.__name__
            if model_name == "type":
                raise AttributeError
        except AttributeError:
            model_name = getattr(model, "__name__")

        return next(
            (
                (pivot_table_name, values[2])
                for pivot_table_name, values in self.CUSTOM_PIVOT_TABLES.items()
                if set(values[:2]) == {model_name, self.__class__.__name__}
            ),
            False,
        )

    def _clean_attachments(self):
        """Cleans up any references to a model instance that's being deleted.
        Called by .delete()."""

        # Get the names of all tables that have a foreign key reference to the current table
        referenced_tables = [
            t
            for t in self.table.get_table_names()
            if self.table.table_name in LiteTable(t).get_foreign_key_references()
        ]

        # Remove references to the current instance from each of the referenced tables
        for t_name in referenced_tables:
            temp_table = LiteTable(t_name)
            key_maps = temp_table.get_foreign_key_references()[self.table.table_name]

            for local_key, foreign_key in key_maps:
                local_key_value = getattr(self, local_key)

                if LiteTable.is_pivot_table(t_name):
                    temp_table.delete([[foreign_key, "=", local_key_value]])
                else:
                    temp_table.update(
                        {foreign_key: None}, [[foreign_key, "=", local_key_value]]
                    )

    def find_path_iter(self, open_n: list, closed_n: list, to_model_inst):
        """Internal method. Step function for .find_path()."""

        if not open_n:
            return False

        current_node = open_n.pop()
        if current_node not in closed_n:
            closed_n.append(current_node)

        if current_node == to_model_inst:
            path = [current_node]
            while temp := getattr(current_node, "parent"):
                path.append(temp)
                current_node = temp

            return list(reversed(path))

        methods = current_node.get_relationship_methods()
        relationship_models = LiteCollection()

        for method in methods:
            if result := getattr(current_node, method)():
                relationship_models = relationship_models + result

        for model in relationship_models:
            setattr(model, "parent", current_node)
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
        instance_variables = set(
            filter(lambda x: x.startswith("_") is False, dir(self))
        )

        # Find all public, *default* LiteModel attributes
        default_variables = set(
            filter(lambda x: x.startswith("_") is False, dir(LiteModel))
        )

        # Determine attributes unique to this particular class
        unique_variables = instance_variables - default_variables

        # Isolate methods from other unique attributes
        unique_methods = []
        for i_var in unique_variables:
            try:
                getattr(getattr(self, i_var), "__call__")
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
            if "return" in method_signature and method_signature["return"] in [
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
        _lite_conn: LiteConnection = None,
    ):
        """LiteModel initializer.
        Parameters are used by internal methods and should not be provided."""

        if not _lite_conn:
            if self.DEFAULT_CONNECTION is not None:
                _lite_conn = self.DEFAULT_CONNECTION
            else:
                _lite_conn = Lite.DEFAULT_CONNECTION

        # Derive table name from class name
        if not hasattr(self, "table_name"):
            self.table_name = self._get_table_name()

        # Load table if not passed
        self.table = _table or LiteTable(self.table_name, _lite_conn)

        # Generate dict map of foreign key references.
        # Used by .get_foreign_key_column_for_model()
        self._foreign_key_map = self.table.get_foreign_key_references()

        # Load model instance from database if an id is provided
        columns = self.table.get_column_names()
        if _id is not None:
            if not _values:
                _values = self.table.select([["id", "=", _id]])

            # Add columns and values to python class instance as attributes
            for col in enumerate(columns):
                value = _values[0][col[0]]
                setattr(self, col[1], value)

            # Store list of all table column names. Used by .save()
        self.table_columns = columns

    @classmethod
    def requires_table(
        cls,
        columns: dict[str, str],
        foreign_keys: dict[str, list[str, str]] = None,
        lite_connection: LiteConnection = None,
    ):
        """
        Creates a database table for the LiteModel if it doesn't exist.

        Args:
            table_name (str): Table name
            columns (dict): {
                column_name: field_attributes
            }
            foreign_keys (dict, optional): {
                column_name: [foreign_table_name, foreign_column_name]
            }
        """

        if not hasattr(cls, "table_name"):
            cls.table_name = cls._get_table_name(cls)

        if not LiteTable.exists(cls.table_name, lite_connection):
            LiteTable.create_table(
                cls.table_name, columns, foreign_keys, lite_connection
            )

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

        table_name = Lite.HelperFunctions.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, "table_name"):
            table_name = cls.table_name

        table = LiteTable(table_name, lite_connection)
        rows = table.select([["id", "=", _id]])

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
            if Lite.DEBUG_MODE:
                print(f"Model instance with id {_id} not found.")
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

        table_name = Lite.HelperFunctions.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, "table_name"):
            table_name = cls.table_name

        table = LiteTable(table_name, lite_connection)

        rows = table.select([], ["id"])
        return LiteCollection([cls.find_or_fail(row[0]) for row in rows])

    @classmethod
    def where(cls, column_name: str) -> LiteQuery:
        """Returns a new LiteQuery instance.

        Args:
            column_name (str): Name of column to query

        Returns:
            LiteCollection: Collection of matching model instances
        """

        return LiteQuery(cls, column_name)

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

        table_name = Lite.HelperFunctions.pluralize_noun(cls.__name__.lower())
        if hasattr(cls, "table_name"):
            table_name = cls.table_name

        # Insert into table
        table = LiteTable(table_name, lite_connection)
        table.insert(column_values)

        # Get latest instance with this id
        sql_str = f"""
            SELECT id FROM {table_name} 
            WHERE {list(column_values.keys())[0]} = ? 
            ORDER BY id DESC
        """

        ids = table.connection.execute(
            sql_str, (column_values[list(column_values.keys())[0]],)
        ).fetchall()

        return cls.find_or_fail(ids[0][0])

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
    def pivots_with(
        cls, other_model, table_name: str, lite_connection: LiteConnection = None
    ):
        """Notifies Lite of a many-to-many relationship.

        Args:
            other_model (LiteModel): The other model forming the many-to-many relationship.
            table_name (str): Name of the pivot table storing the relationships.
            lite_connection (LiteConnection, optional):
                A connection to the database in which the pivot table is stored. If the pivot table
                exists in the same database as the models, this argument can be omitted.
        """

        if lite_connection is None and cls.DEFAULT_CONNECTION is not None:
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
                attribute = f"{attribute[:50]}..."

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
            pivot_table_name, lite_connection = self._get_pivot_name(model_instance)
        except (RelationshipError, AttributeError, TypeError):
            pivot_table_name = False

        if pivot_table_name:  # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name, lite_connection)

            # Derive foreign keys from pivot table
            foreign_keys = pivot_table.get_foreign_key_references()

            # user should provide a self and model foreign keys if the pivot
            # table associates two rows from the *same* table
            if not self_fkey or not model_fkey:
                if (
                    model_instance.table_name == self.table_name
                    and len(foreign_keys[self.table_name]) > 1
                ):
                    model_fkey = foreign_keys[model_instance.table_name][1][1]
                else:
                    model_fkey = foreign_keys[model_instance.table_name][0][1]

                self_fkey = foreign_keys[self.table_name][0][1]

            # Make sure this relationship doesn't already exist
            relationships = pivot_table.select(
                [[self_fkey, "=", self.id], [model_fkey, "=", model_instance.id]]
            )

            # Insert relationship into pivot table
            if len(relationships) == 0:
                pivot_table.insert({self_fkey: self.id, model_fkey: model_instance.id})
            else:
                raise RelationshipError("This relationship already exists.")

            return True

        # Is not a many-to-many relationship
        # Derive foreign keys
        try:
            self_fkey = model_instance.get_foreign_key_column_for_model(self)
        except AttributeError as exc:
            raise TypeError("The passed model instance is not a LiteModel.") from exc
        model_fkey = self.get_foreign_key_column_for_model(model_instance)

        # Determine which model instance contains the reference to the other,
        # and make sure a relationship doesn't already exist.
        if model_fkey in self.table_columns:  # self contains foreign key reference
            if getattr(self, model_fkey) is not None:
                raise RelationshipError(
                    """There is a pre-existing relationship. 
                    Remove it with .detach() before proceeding."""
                )
            setattr(self, model_fkey, model_instance.id)
            self.save()
        elif hasattr(
            model_instance, self_fkey
        ):  # model_instance contains foreign key reference
            if getattr(model_instance, self_fkey) is not None:
                raise RelationshipError(
                    """There is a pre-existing relationship.
                    Remove it with .detach() before proceeding."""
                )
            setattr(model_instance, self_fkey, self.id)
            model_instance.save()
        else:
            raise RelationshipError(
                """Parent model has no relation to the passed model. 
                Be sure that foreign keys reference the correct table names."""
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
            pivot_table_name, lite_connection = self._get_pivot_name(model_instance)
        except (AttributeError, TypeError):
            pivot_table_name = False

        if pivot_table_name:  # Is a many-to-many relationship
            return self._detach_from_pivot_table(
                pivot_table_name, lite_connection, model_instance
            )

        # Is not many-to-many relationship
        # Derive foreign keys
        try:
            self_fkey = model_instance.get_foreign_key_column_for_model(self)
        except AttributeError as exc:
            raise TypeError("The passed model instance is not a LiteModel.") from exc
        model_fkey = self.get_foreign_key_column_for_model(model_instance)

        # Determine which model instance contains the reference to the other
        if model_fkey in self.table_columns:
            if getattr(self, model_fkey) != model_instance.id:
                raise RelationshipError("Relationship does not exist. Cannot detach.")
            setattr(self, model_fkey, None)
            self.save()
        elif getattr(model_instance, self_fkey) == self.id:
            setattr(model_instance, self_fkey, None)
            model_instance.save()
        else:
            raise RelationshipError("Relationship does not exist. Cannot detach.")

        return True

    def _detach_from_pivot_table(
        self, pivot_table_name, lite_connection, model_instance
    ):
        """Removes a relationship between two model instances from a pivot table."""

        pivot_table = LiteTable(pivot_table_name, lite_connection)

        # Derive foreign keys
        foreign_keys = pivot_table.get_foreign_key_references()

        model_fkey = (
            foreign_keys[model_instance.table_name][1][1]
            if (
                model_instance.table_name == self.table_name
                and len(foreign_keys[self.table_name]) > 1
            )
            else foreign_keys[model_instance.table_name][0][1]
        )
        self_fkey = foreign_keys[self.table_name][0][1]

        # Make sure this relationship doesn't already exist
        if (
            len(
                pivot_table.select(
                    [[self_fkey, "=", self.id], [model_fkey, "=", model_instance.id]]
                )
            )
            < 1
        ):
            raise RelationshipError("Relationship does not exist. Cannot detach.")

        pivot_table.delete(
            [[self_fkey, "=", self.id], [model_fkey, "=", model_instance.id]]
        )

        return True

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
            raise ModelInstanceNotFoundError(self.id)

        # Take care of attachments that stick around after deleting the model instance
        self._clean_attachments()

        self.table.delete([["id", "=", self.id]])

        for column in self.table_columns:
            setattr(self, column, None)

    def save(self):
        """Saves any changes to model instance attributes."""

        update_columns = {
            column: getattr(self, column)
            for column in self.table_columns
            if column not in ["id", "created", "updated"]
        }

        if self.id is None:  # Create model if no id is provided
            self.table.insert(update_columns)
            self.id = (
                self.__class__().all().sort("id").last().id
            )  # Get id of last inserted row
        else:
            self.table.update(update_columns, [["id", "=", self.id]])

    def fresh(self):
        """Reloads the model's attributes from the database."""

        # Load model instance from database by primary key
        values = self.table.select([["id", "=", self.id]])

        # Set attributes of Python class instance
        for index, column in enumerate(self.table_columns):
            value = values[0][index]
            setattr(self, column, value)

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
            foreign_key = self.get_foreign_key_column_for_model(model)

        # Get database row ID of parent model
        parent_model_id = getattr(self, foreign_key)

        return model.find(parent_model_id)

    def get_pivot_table(self, model):
        """Returns the pivot table for a given sibling model."""

        model_class_name = getattr(model, "__name__").lower()
        if model_class_name not in self.PIVOT_TABLE_CACHE:
            pivot_table_name, lite_connection = self._get_pivot_name(model)
            pivot_table = LiteTable(pivot_table_name, lite_connection)
            foreign_keys = pivot_table.get_foreign_key_references()
            self.PIVOT_TABLE_CACHE[model_class_name] = [foreign_keys, pivot_table]
        else:
            foreign_keys, pivot_table = self.PIVOT_TABLE_CACHE[model_class_name]
        return foreign_keys, pivot_table

    def get_foreign_key_column_names(self, foreign_keys, model_instance):
        """Returns the foreign keys for a given model instance."""

        if (
            model_instance.table_name == self.table_name
            and len(foreign_keys[self.table_name]) > 1
        ):
            self_fkey = [
                foreign_keys[self.table_name][0][1],
                foreign_keys[self.table_name][1][1],
            ]
            model_fkey = [
                foreign_keys[model_instance.table_name][1][1],
                foreign_keys[model_instance.table_name][0][1],
            ]
        else:
            self_fkey = foreign_keys[self.table_name][0][1]
            model_fkey = foreign_keys[model_instance.table_name][0][1]
        return self_fkey, model_fkey

    def get_relationships(self, pivot_table, self_fkey, model_fkey):
        """Returns the many-to-many relationships for a given pivot table,
        self foreign key, and model foreign key."""

        if not isinstance(self_fkey, list):
            return pivot_table.connection.execute(
                f"""
                SELECT {model_fkey} 
                FROM {pivot_table.table_name} 
                WHERE {self_fkey} = {self.id}
            """
            ).fetchall()
        select_queries = [
            f"""
                    SELECT {model_fkey[i]} 
                    FROM {pivot_table.table_name} 
                    WHERE {self_fkey[i]} = {self.id}
                """
            for i in range(len(self_fkey))
        ]
        return pivot_table.connection.execute(" UNION ".join(select_queries)).fetchall()

    def belongs_to_many(self, model) -> LiteCollection:
        """Defines a many-to-many relationship between the current model instance and a model class.

        Args:
            model (LiteModel): Sibling model class

        Returns:
            LiteCollection: Sibling model instances
        """

        foreign_keys, pivot_table = self.get_pivot_table(model)
        model_instance = model()

        self_fkey, model_fkey = self.get_foreign_key_column_names(
            foreign_keys, model_instance
        )

        relationships = self.get_relationships(pivot_table, self_fkey, model_fkey)

        siblings_collection = []
        for rel in relationships:
            if sibling := model.find(rel[0]):
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
        if not hasattr(model, "table_name"):
            model.table_name = Lite.HelperFunctions.pluralize_noun(
                model.__name__.lower()
            )

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key:
            foreign_key = model_instance.get_foreign_key_column_for_model(self)

        child_table = LiteTable(model.table_name)
        child_ids = child_table.select([[foreign_key, "=", self.id]], ["id"])

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

        model_instance = model()

        # Derive foreign and local keys if none are provided
        if not foreign_key:
            foreign_key = model_instance.get_foreign_key_column_for_model(self)

        child_table = LiteTable(model.table_name, model.DEFAULT_CONNECTION)
        child_rows = child_table.select([[foreign_key, "=", self.id]], ["id"])

        children_collection = [model.find(row[0]) for row in child_rows]
        return LiteCollection(children_collection)

    def find_path(self, to_model_instance, max_depth: int = 100):
        """Attempts to find a path from the current model instance
        to another using Bidirectional BFS.

        Args:
            to_model_instance (LiteModel): Model instance to navigate to
            max_depth (int, optional): Maximum depth to traverse. Defaults to 100.

        Returns:
            LiteCollection or bool: Either the path or False for failure
        """

        setattr(self, "parent", None)
        setattr(to_model_instance, "parent", None)

        open_nodes = [self]
        reversed_open_nodes = [to_model_instance]
        closed_nodes = []
        reversed_closed_nodes = []

        for _ in range(max_depth):
            path = self.find_path_iter(open_nodes, closed_nodes, to_model_instance)
            if path is not False:
                return path

            reversed_path = to_model_instance.find_path_iter(
                reversed_open_nodes, reversed_closed_nodes, self
            )
            if reversed_path is not False:
                return list(reversed(reversed_path))

        return LiteCollection([])
