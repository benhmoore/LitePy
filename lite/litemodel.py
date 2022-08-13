import re, typing
from lite import *

class LiteModel:
    """Describes a distinct model for database storage and methods for operating upon it.

    Raises:
        TypeError: Comparison between incompatible types.
        ModelInstanceNotFoundError: Model does not exist in database.
        RelationshipError: Relationship does not match required status.
    """
    DEFAULT_CONNECTION = None # Overridden by LiteModel.connect()
    CUSTOM_PIVOT_TABLES = {} # Filled by calls to .pivotsWith()
    PIVOT_TABLE_CACHE = {} # Used by belongsToMany() to cache pivot table names and foreign keys


    def __str__(self): return self._toDict().__str__()


    def __repr__(self):
        attributes = []
        for key in self.table_columns:
            attributes.append(getattr(self,key))

        return str(tuple(attributes))


    def __lt__(self, other):
        try: getattr(other, 'id')
        except: raise TypeError
        
        if self.id < other.id:
            return True
        else:
            return False


    def __eq__(self, other):
        # Collect base classes of class being compared to make sure it is a LiteModel
        base_classes = []
        for bc in other.__class__.__bases__:
            base_classes.append(bc.__name__)

        if 'LiteModel' in base_classes:
            if self.table.table_name == other.table.table_name:
                if self.table_columns == other.table_columns:

                    for col in self.table_columns:
                        if getattr(self, col) != getattr(other, col): # If any column differs in value, these instances are not equal
                            return False
                    
                    return True
        return False


    def __pluralize(self, noun:str) -> str:
        """Returns plural form of noun. Used for table name derivations.

        Algorithm sourced from: https://linux.die.net/diveintopython/html/dynamic_functions/stage1.html

        Args:
            noun (str): Singular noun

        Returns:
            str: Plural noun
        """
        if re.search('[sxz]$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('[^aeioudgkprt]h$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('[aeiou]y$', noun):
            return re.sub('y$', 'ies', noun)
        else:
            return noun + 's'


    def __get_table_name(self) -> str:
        """Returns the derived table name by getting the plural noun form of the LiteModel instance's name.

        Returns:
            str: Derived table name
        """

        return self.__pluralize(self.__class__.__name__.lower())


    def __has_column(self, column_name:str) -> bool:
        """Checks if LiteModel instance has a given field or column.

        Args:
            column_name (str): Field name to look for

        Returns:
            bool
        """
        
        if column_name in self.table_columns:
            return True
        else:
            return False


    def __get_foreign_key_from_model(self, model) -> str:
        """Derives name of foreign key within current instance that references passed-in model.

        This is used to get the `primary key` value of the parent or child to this model.
        For example, if a `User` belongs to an `Account`, calling this method on `User`
        and passing in `Account` would return the name of the foreign key column referencing
        the particular `Account` instance the current `User` belongs to.

        - Called by attach(), detach(), belongsTo(), hasOne(), and hasMany().

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            str: Name of foreign key column referencing `parent` model instance.
        """
        
        # Get conventional foreign key name and table name
        try: # Passed model is actually an instance
            self_fkey = f'{model.__class__.__name__.lower()}_id'
            model_table_name = model.TABLE_NAME
        except: # Passed model is a LiteModel class
            self_fkey = f'{model.__name__.lower()}_id'
            model_table_name = self.__pluralize(model.__name__.lower())

        # Check if this table has a custom foreign key column name 
        if model_table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_table_name][0][1]

        return self_fkey


    def __get_pivot_name(self, model) -> str:
        """Returns the pivot table between `self` and the given LiteModel instance or class, if it exists.

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            str: Name of pivot table
        """

        # Check CUSTOM_PIVOT_TABLES for any pivot tables with custom names that define relationships between these two models
        self_name = self.__class__.__name__
        try: 
            model_name = model.__class__.__name__
            if model_name == 'type': raise Exception
        except: model_name = getattr(model, '__name__')

        for name in self.CUSTOM_PIVOT_TABLES:
            if self.CUSTOM_PIVOT_TABLES[name][:2] == [model_name, self_name] or self.CUSTOM_PIVOT_TABLES[name][:2] == [self_name, model_name]:
                lite_connection = self.CUSTOM_PIVOT_TABLES[name][2]
                return name, lite_connection

        # Otherwise, derive conventional naming scheme for pivot tables
        # This table must be stored in the database denoted by Lite's DEFAULT CONNECTION

        model_names = []
        model_names.append(self.__class__.__name__.lower())

        try: model_name = getattr(model, '__name__').lower()
        except: model_name = model.__class__.__name__.lower()

        model_names.append(model_name)

        model_names = sorted(model_names) # Make alphabetical
        pivot_table_name = '_'.join(model_names) # Join into string of format 'model_model'

        # Check to see if table with this name exists
        if LiteTable.isPivotTable(pivot_table_name):
            return pivot_table_name, None # If it does, return the table name

    def __clean_attachments(self):
        """Internal method. Cleans up any references to a model instance that's being deleted. Called by .delete()."""

        foreign_keys = self.table.getForeignKeyReferences()
        table_names = self.table.getAllTableNames()

        check_tables = {}

        for t_name in table_names:
            temp_table = LiteTable(t_name)

            temp_foreign_keys = temp_table.getForeignKeyReferences()

            if self.table.table_name in temp_foreign_keys:
                check_tables[temp_table.table_name] = temp_foreign_keys[self.table.table_name]

        for tName in check_tables:
            # Get local and foreign keys
            key_maps = check_tables[tName]
            for i in range(0, len(key_maps)):
                local_key = key_maps[i][0]
                foreign_key = key_maps[i][1]

                local_key_value = getattr(self, local_key)

                # Check if table is a pivot table, as detach procedure will be different
                temp_table = LiteTable(tName)
                if LiteTable.isPivotTable(tName):
                    temp_table.delete([[foreign_key,'=',local_key_value]])
                else:
                    temp_table.update({foreign_key: None}, [[foreign_key,'=',local_key_value]])
                

    def __findPath__iteration(self, open_nodes:list, closed_nodes:list, to_model_instance):
        """Internal method. Step function for .findPath()."""

        if len(open_nodes) < 1: return False

        q = open_nodes.pop()
        if q not in closed_nodes: closed_nodes.append(q)

        if q == to_model_instance: # Calculate and return path
            
            path = [q]
            temp = getattr(q,'parent')
            while temp != None:
                path.append(temp)
                temp = getattr(temp,'parent')

            return list(reversed(path))

        # Get relationship definition methods
        methods = q.__get_relationship_methods()

        relationship_models = LiteCollection()
        
        for method in methods:
            result = getattr(q, method)()
            if result:
                if type(result) == LiteCollection:
                    try: relationship_models.join(result)
                    except: pass
                else:
                    try: relationship_models.add(result)
                    except: pass

        for model in relationship_models:
            
            setattr(model, 'parent', q) # Set special parent attribute to keep track of path
            if model in closed_nodes: continue

            open_nodes.insert(0, model) # insert to beginning of open_nodes

        return False


    def __get_relationship_methods(self) -> list:
        """Returns a list of method names that define model-model relationships.

        To ensure methods are correctly identified as relationship definitions,
        make sure to specify a return type of `LiteCollection` or `LiteModel` when
        defining them.

        Returns:
            list: List of method names as strings
        """

        # Find all public attributes of this class
        instance_variables = set(filter(lambda x: x.startswith('_') == False, dir(self)))

        # Find all public, *default* LiteModel attributes
        default_variables = set(filter(lambda x: x.startswith('_') == False, dir(LiteModel)))

        # Determine attributes unique to this particular class
        unique_variables = instance_variables - default_variables
        
        # Isolate methods from other unique attributes
        unique_methods = []
        for i_var in unique_variables:
            try: 
                getattr(getattr(self, i_var), '__call__')
                unique_methods.append(i_var)
            except: continue
                
        # These methods should contain any relationship definitions (hasOne, hasMany, belongsToMany, etc.)
        # To find these relationship definitions, look for methods that return either a LiteCollection or a LiteModel:
        relationship_definitions = []
        for method in unique_methods:
            method_signature = typing.get_type_hints(getattr(self, method))

            # Make sure return type is specified by method, and that it is a LiteCollection or LiteModel
            if "return" in method_signature:
                if method_signature['return'] == LiteCollection or method_signature['return'] == LiteModel:
                    relationship_definitions.append(method)
        
        return relationship_definitions


    def __init__(self, _id:int=None, _table:LiteTable=None, _values:list=None, _lite_connection:LiteConnection=None):
        """LiteModel initializer. Parameters are used by internal methods and should not be provided."""

        if not _lite_connection: 
            if self.DEFAULT_CONNECTION is not None:
                _lite_connection = self.DEFAULT_CONNECTION
            else:
                _lite_connection = Lite.DEFAULT_CONNECTION

        # Derive table name from class name
        if not hasattr(self, 'TABLE_NAME'): self.TABLE_NAME = self.__get_table_name()

        # Load table if not passed
        self.table = _table or LiteTable(self.TABLE_NAME, _lite_connection)

        # Generate dict map of foreign key references. Used by .__get_foreign_key_from_model()
        self.FOREIGN_KEY_MAP = self.table.getForeignKeyReferences()

        # Load model instance from database if an id is provided
        if _id != None:

            columns = self.table.getColumnNames()

            if not _values: _values = self.table.select([['id','=',_id]])

            # Add columns and values to python class instance as attributes
            for i in range(0,len(columns)):
                try: value = _values[0][i]
                except: value = None
                setattr(self, columns[i], value)
                
            # Store list of all table column names. Used by .save()
            self.table_columns = columns


    @classmethod
    def findOrFail(self, id:int):
        """Returns a LiteModel instance with id matching the passed value. Throws an exception if an instance isn't found.

        Args:
            id (int): Id of model instance within database table

        Raises:
            ModelInstanceNotFoundError: Model does not exist in database.

        Returns:
            LiteModel: LiteModel with matching id
        """

        if self.DEFAULT_CONNECTION is not None:
            lite_connection = self.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        TABLE_NAME = self.__pluralize(self,self.__name__.lower())
        if hasattr(self, 'TABLE_NAME'): TABLE_NAME = self.TABLE_NAME
        
        table = LiteTable(TABLE_NAME, lite_connection)
        rows = table.select([['id','=',id]])

        if len(rows) > 0: return self(id, table, rows, lite_connection) # Return LiteModel
        else: 
            raise ModelInstanceNotFoundError(id)


    @classmethod
    def find(self, id:int):
        """Returns a LiteModel instance with id matching the passed value or None.

        Args:
            id (int): Id of model instance within database table

        Returns:
            LiteModel: LiteModel with matching id or None
        """

        try:
            return self.findOrFail(id)
        except ModelInstanceNotFoundError:
            return None


    @classmethod
    def all(self) -> LiteCollection:
        """Returns a LiteCollection containing all instances of this model.

        Returns:
            LiteCollection: Collection of all model instances
        """
        
        if self.DEFAULT_CONNECTION is not None:
            lite_connection = self.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        TABLE_NAME = self.__pluralize(self,self.__name__.lower())
        if hasattr(self, 'TABLE_NAME'): TABLE_NAME = self.TABLE_NAME
        
        table = LiteTable(TABLE_NAME, lite_connection)

        collection = []
        rows = table.select([],['id'])
        for row in rows:
            collection.append(self.findOrFail(row[0]))
        
        return LiteCollection(collection)


    @classmethod
    def where(self, where_columns:list) -> LiteCollection:
        """Returns a LiteCollection containing all model instances matching where_columns.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            LiteCollection: Collection of matching model instances
        """ 

        if self.DEFAULT_CONNECTION is not None:
            lite_connection = self.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION
        
        TABLE_NAME = self.__pluralize(self,self.__name__.lower())
        if hasattr(self, 'TABLE_NAME'): TABLE_NAME = self.TABLE_NAME
        
        table = LiteTable(TABLE_NAME, lite_connection)

        collection = []
        rows = table.select(where_columns,['id'])
        for row in rows:
            collection.append(self.findOrFail(row[0]))
        
        return LiteCollection(collection)


    @classmethod
    def create(self, column_values:dict):
        """Creates a new instance of a LiteModel and returns it.

        Args:
            column_values (dict): The initial values to be stored for this model instance.

        Returns:
            LiteModel: Created model instance.
        """

        if self.DEFAULT_CONNECTION is not None:
            lite_connection = self.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION
        
        TABLE_NAME = self.__pluralize(self,self.__name__.lower())
        if hasattr(self, 'TABLE_NAME'): TABLE_NAME = self.TABLE_NAME
        
        # Insert into table
        table = LiteTable(TABLE_NAME, lite_connection)
        table.insert(column_values)

        # Get latest instance with this id
        if table.connection.connection_type == DB.SQLITE:
            sql_str = f'SELECT id FROM {TABLE_NAME} WHERE {list(column_values.keys())[0]} = ? ORDER BY id DESC'
        elif table.connection.connection_type == DB.POSTGRESQL:
            sql_str = f'SELECT id FROM {TABLE_NAME} WHERE {list(column_values.keys())[0]} = %s ORDER BY id DESC'

        ids = table.connection.execute(sql_str, tuple([column_values[list(column_values.keys())[0]]])).fetchall()

        # This check should never fail
        if len(ids) > 0:
            return self.findOrFail(ids[0][0])
        else:
            raise Exception('Could not locate model that was created.')


    @classmethod
    def createMany(self, column_list:list) -> LiteCollection:
        """Creates many new instances of a LiteModel and returns them within a LiteCollection.

        Args:
            column_values (dict): The initial values to be stored for this model instance.

        Returns:
            LiteCollection: Created model instances.
        """
        
        model_list = []
        for column_set in column_list:
            model_list.append(self.create(column_set))
        
        return LiteCollection(model_list)


    @classmethod
    def pivotsWith(self, other_model, table_name:str, lite_connection:LiteConnection=None):
        """Notifies Lite of a many-to-many relationship. This is only required when a custom pivot table name is used.

        Args:
            other_model (LiteModel): The other model forming the many-to-many relationship.
            table_name (str): Name of the pivot table storing the relationships.
        """

        if not lite_connection: 
            if self.DEFAULT_CONNECTION is not None:
                _lite_connection = Lite.DEFAULT_CONNECTION

        self_name = self.__name__
        other_name = other_model.__name__

        self.CUSTOM_PIVOT_TABLES[table_name] = [self_name, other_name, lite_connection]


    @classmethod
    def accessedThrough(self, lite_connection:LiteConnection):
        """Declares the connection Lite should use for this model.

        Args:
            lite_connection (LiteConnection): Connection pointed to the database in which this model is stored
        """
        self.DEFAULT_CONNECTION = lite_connection


    def _toDict(self) -> dict:
        """Internal method. Converts LiteModel instance into human-readable dict, truncating string values where necessary.

        Returns:
            dict: LiteModel attributes as dictionary
        """
        
        print_dict = {}

        for column in self.table_columns:
            attribute = getattr(self, column)

            # Convert byte strings to regular strings
            if type(attribute) == bytes: attribute = attribute.decode("utf-8") 

            # Truncate text over 50 characters)
            if type(attribute) == str:
                if len(attribute) > 50: attribute = attribute[:50] + '...'
            print_dict[column] = attribute

        return print_dict


    def attach(self, model_instance, self_fkey:str=None, model_fkey:str=None):
        """Defines a relationship between two model instances.

        Args:
            model_instance (LiteModel): Model instance to attach to self.

        Raises:
            RelationshipError: Relationship already exists.
        """

        try: pivot_table_name, lite_connection = self.__get_pivot_name(model_instance)
        except: pivot_table_name = False

        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name, lite_connection)

            # Derive foreign keys from pivot table
            foreign_keys = pivot_table.getForeignKeyReferences()

            # user should provide a self and model foreign keys if the pivot table associates two rows from the *same* table
            if not self_fkey or not model_fkey:
                if model_instance.TABLE_NAME == self.TABLE_NAME and len(foreign_keys[self.TABLE_NAME]) > 1:
                    self_fkey = foreign_keys[self.TABLE_NAME][0][1]
                    model_fkey = foreign_keys[model_instance.TABLE_NAME][1][1]
                else:
                    self_fkey = foreign_keys[self.TABLE_NAME][0][1]
                    model_fkey = foreign_keys[model_instance.TABLE_NAME][0][1]

            # Make sure this relationship doesn't already exist
            relationships = pivot_table.select([[self_fkey,'=',self.id], [model_fkey,'=',model_instance.id]])

            # Insert relationship into pivot table
            if len(relationships) == 0:
                pivot_table.insert({
                    self_fkey: self.id,
                    model_fkey: model_instance.id
                })
            else:
                raise RelationshipError(f"This relationship already exists.")

            return True
            
        else: # Is not a many-to-many relationship

            # Derive foreign keys
            self_fkey = model_instance.__get_foreign_key_from_model(self)
            model_fkey = self.__get_foreign_key_from_model(model_instance)

            # Determine which model instance contains the reference to the other, and make sure a relationship doesn't already exist.
            if self.__has_column(model_fkey): # self contains foreign key reference
                if getattr(self, model_fkey) == None:
                    setattr(self, model_fkey, model_instance.id)
                    self.save()
                else:
                    raise RelationshipError(f"There is a pre-existing relationship. Remove it with .detach() before proceeding.")

            else: # model_instance contains foreign key reference
                if getattr(model_instance, self_fkey) == None:
                    setattr(model_instance, self_fkey, self.id)
                    model_instance.save()
                else:
                    raise RelationshipError(f"There is a pre-existing relationship. Remove it with .detach() before proceeding.")

        return True


    def attachMany(self, model_instances):
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
        
        try: pivot_table_name, lite_connection = self.__get_pivot_name(model_instance)
        except: pivot_table_name = False

        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name, lite_connection)
            
            # Derive foreign keys
            foreign_keys = pivot_table.getForeignKeyReferences()

            if model_instance.TABLE_NAME == self.TABLE_NAME and len(foreign_keys[self.TABLE_NAME]) > 1:
                self_fkey = foreign_keys[self.TABLE_NAME][0][1]
                model_fkey = foreign_keys[model_instance.TABLE_NAME][1][1]
            else:
                self_fkey = foreign_keys[self.TABLE_NAME][0][1]
                model_fkey = foreign_keys[model_instance.TABLE_NAME][0][1]

            # Make sure this relationship doesn't already exist
            relationships = pivot_table.delete([
                [self_fkey,'=',self.id],
                [model_fkey,'=',model_instance.id]
            ])

        else: # Is not many-to-many relationship
            # Derive foreign keys
            self_fkey = model_instance.__get_foreign_key_from_model(self)
            model_fkey = self.__get_foreign_key_from_model(model_instance)
            
            # Determine which model instance contains the reference to the other
            if self.__has_column(model_fkey):
                if (getattr(self, model_fkey) == model_instance.id):
                    setattr(self, model_fkey, None)
                    self.save()
                else:
                    raise RelationshipError(f"Relationship does not exist. Cannot detach.")
            else:
                if (getattr(model_instance, self_fkey) == self.id):
                    setattr(model_instance, self_fkey, None)
                    model_instance.save()
                else:
                    raise RelationshipError(f"Relationship does not exist. Cannot detach.")


    def detachMany(self, model_instances):
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

        if self.id == None: raise ModelInstanceNotFoundError(self.id) # Cannot delete a model instance that isn't saved in database

        self.__clean_attachments() # Remove any attachments that would otherwise stick around after deleting the model instance

        self.table.delete([['id','=',self.id]])

        # Since the python object instance cannot be removed from memory manually,
        # set all attributes to None
        for column in self.table_columns: setattr(self, column, None)
        

    def save(self):
        """Saves any changes to model instance attributes."""

        update_columns = {}
        for column in self.table_columns:
            if column == 'id': continue # Don't update or insert id directly
            update_columns[column] = getattr(self, column)

        if self.id == None: # Create model if no id is provided
            self.table.insert(update_columns)
        else:
            self.table.update(update_columns,[['id','=',self.id]])


    def fresh(self):
        """Reloads the model's attributes from the database."""

        # Load model instance from database by primary key
        _values = self.table.select([['id','=',self.id]])

        # Set attributes of Python class instance
        for i in range(0,len(self.table_columns)):
            try: value = _values[0][i]
            except: value = None
            setattr(self, self.table_columns[i], value)


    def belongsTo(self, model, foreign_key:str=None):
        """Defines the current model instance as a child of the passed model class.

        Args:
            model (LiteModel): Parent model class
            foreign_key (str, optional): Custom foreign key name. Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteModel: Parent model instance
        """

        # Derive foreign key if not provided
        if not foreign_key: foreign_key = self.__get_foreign_key_from_model(model)

        # Get database row ID of parent model
        parent_model_id = getattr(self, foreign_key)

        return model.find(parent_model_id)


    def belongsToMany(self, model) -> LiteCollection: # Many-to-many
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
            foreign_keys = pivot_table.getForeignKeyReferences()

            self.PIVOT_TABLE_CACHE[model_class_name] = [foreign_keys, pivot_table]     
        else: # If the pivot table for this relationship is already in the cache, use it
            foreign_keys, pivot_table = self.PIVOT_TABLE_CACHE[model_class_name]

        model_instance = model()

        # Handles pivot tables that relate two of the same model
        if model_instance.TABLE_NAME == self.TABLE_NAME and len(foreign_keys[self.TABLE_NAME]) > 1:
            self_fkey = [foreign_keys[self.TABLE_NAME][0][1],foreign_keys[self.TABLE_NAME][1][1]]
            model_fkey = [foreign_keys[model_instance.TABLE_NAME][1][1],foreign_keys[model_instance.TABLE_NAME][0][1]]
        else:
            self_fkey = foreign_keys[self.TABLE_NAME][0][1]
            model_fkey = foreign_keys[model_instance.TABLE_NAME][0][1]

        # Assume relationship is many-to-many
        siblings_collection = []
        relationships = []

        if type(self_fkey) == list:
            select_queries = []
            for i in range(0, len(self_fkey)):
                select_queries.append(f'SELECT {model_fkey[i]} FROM {pivot_table.table_name} WHERE {self_fkey[i]} = {self.id}')
            relationships = pivot_table.connection.execute(' UNION '.join(select_queries)).fetchall()
        else:
            relationships = pivot_table.connection.execute(f'SELECT {model_fkey} FROM {pivot_table.table_name} WHERE {self_fkey} = {self.id}').fetchall()

        for rel in relationships:
            try: sibling = model.find(rel[0])
            except ModelInstanceNotFoundError: continue
            siblings_collection.append(sibling)

        return LiteCollection(siblings_collection)


    def hasOne(self, model, foreign_key:str=None): # One-to-one
        """Reverse of belongsTo. Defines the current model instance as a parent of the passed model class.

        Args:
            model (LiteModel): Child model class
            foreign_key (str, optional): Custom foreign key name. Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteModel: Child model instance
        """

        # Get table name of model
        if not hasattr(model, 'TABLE_NAME'): model.TABLE_NAME = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_model(self)

        child_table = LiteTable(model.TABLE_NAME)
        child_ids = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])
        
        if len(child_ids) > 0:
            return model.find(child_ids[0][0])
        else:
            return None


    def hasMany(self, model, foreign_key:str=None) -> LiteCollection: # One-to-many
        """Defines the current model instance as a parent of many of the passed model class.

        Args:
            model (LiteModel): Children model class
            foreign_key (str, optional): Custom foreign key name. Defaults to standard naming convention, 'model_id'.

        Returns:
            LiteCollection: Children model instances
        """

        # Get table name of model
        if not hasattr(model, 'TABLE_NAME'): model.TABLE_NAME = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_model(self)
        
        child_table = LiteTable(model.TABLE_NAME, model.DEFAULT_CONNECTION)
        child_rows = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])

        children_collection = []
        for row in child_rows:
            children_collection.append(model.find(row[0]))

        return LiteCollection(children_collection)


    def findPath(self, to_model_instance, max_depth:int=100):
        """Attempts to find a path from the current model instance to another. Uses Bidirectional BFS.

        Args:
            to_model_instance (LiteModel): Model instance to navigate to
            max_depth (int, optional): Maximum depth to traverse. Defaults to 100.

        Returns:
            LiteCollection or bool: Either the path or False for failure
        """

        # Lists used to measure speed of path finding algorithms in real time
        n_times = []
        r_times = []

        setattr(self, 'parent', None)
        setattr(to_model_instance, 'parent', None)

        open_nodes = []
        open_nodes.append(self)

        reversed_open_nodes = []
        reversed_open_nodes.append(to_model_instance)

        closed_nodes = []
        reversed_closed_nodes = []

        iterations = 0
        while iterations < max_depth:
            path = self.__findPath__iteration(open_nodes, closed_nodes, to_model_instance)
            if path is not False: return LiteCollection(path)

            reversed_path = to_model_instance.__findPath__iteration(reversed_open_nodes, reversed_closed_nodes, self)
            if reversed_path is not False: return LiteCollection(reversed(reversed_path))

            iterations += 1

        return LiteCollection([])

