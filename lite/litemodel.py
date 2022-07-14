import re, typing
from lite import *

class LiteCollection:
    """Container for LiteModel instances. Provides useful methods and overloads for common operations."""

    def __init__(self, model_instances:list=None):
        """Initializes new LiteCollection with given list of LiteModel instances.

        Args:
            model_instances (list, optional): List of LiteModel instances. Defaults to None.
        """        
        self.list = []
        if model_instances: 
            for instance in model_instances:
                if instance not in self.list: self.list.append(instance)


    def __str__(self):
        print_list = []
        for model_instance in self.list:
            print_list.append(model_instance.toDict())
        return print_list.__str__()


    def __len__(self):
        return len(self.list)


    def __eq__(self, other):
        if other.__class__.__name__ == 'LiteCollection':
            if self.list == other.list:
                return True
            else:
                return False
        elif other.__class__.__name__ == 'list':
            if self.list == other:
                return True
            else:
                return False


    def __contains__(self, item):
        if item in self.list:
            return True
        else:
            return False


    def __getitem__(self, item): return self.list[item]


    def add(self, model_instance):
        """Adds a LiteModel instance to the collection.

        Args:
            model_instance (LiteModel): LiteModel instance

        Raises:
            DuplicateModelInstance: Model instance already exists in LiteCollection
        """

        # Check if LiteModel instance is already in this collection
        if model_instance in self.list: raise DuplicateModelInstance(model_instance)

        self.list.append(model_instance)
            

    def join(self, lite_collection):
        """Merges two LiteCollection instances.

        Args:
            lite_collection (LiteCollection): LiteCollection instance
        """
        
        self.list += lite_collection.list


    def remove(self, model_instance):
        """Removes a LiteModel instance from this collection.

        Args:
            model_instance (LiteModel): LiteModel instance to remove

        Raises:
            ModelInstanceNotFoundError: LiteModel instance does not exist in this collection.
        """

        try: self.list.remove(model_instance)
        except: raise ModelInstanceNotFoundError(model_instance.id)


    def where(self, where_columns:list):
        """Simulates a select query on this collection.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            LiteCollection: Matching LiteModel instances
        """

        results_collection = []
        for model in self.list:
            should_add = True
            for condition in where_columns:
                if condition[1] == '=':
                    if getattr(model,condition[0]) != condition[2]:
                        should_add = False
                elif condition[1] == '!=':
                    if getattr(model,condition[0]) == condition[2]:
                        should_add = False
                elif condition[1] == 'LIKE':
                    if condition[2][1:-1] not in getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == 'NOT LIKE':
                    if condition[2][1:-1] in getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == '<':
                    if condition[2] < getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == '>':
                    if condition[2] > getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
            if should_add: results_collection.append(model)

        return LiteCollection(results_collection)


class LiteModel:


    PIVOT_TABLE_CACHE = {} # Used by belongsToMany() to cache pivot table names and foreign keys

    def toDict(self) -> dict:
        """Converts LiteModel instance into human-readable dict, truncating string values where necessary.

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


    def __str__(self): return self.toDict().__str__()


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


    # def get_foreign_key_references(self):
    #     foreign_keys = self.table.execute_and_fetch(f'PRAGMA foreign_key_list({self.table_name})')

    #     foreign_key_map = {}

    #     for fkey in foreign_keys:
    #         table_name = fkey[2]
    #         foreign_key = fkey[3]
    #         local_key = fkey[4]

    #         if table_name not in foreign_key_map: foreign_key_map[table_name] = []

    #         foreign_key_map[table_name].append([local_key, foreign_key])
            
    #     return {}


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
            model_table_name = model.table_name

        except: # Passed model is a LiteModel class
            self_fkey = f'{model.__name__.lower()}_id'
            model_table_name = self.__pluralize(model.__name__.lower())

        # Check if this table has a custom foreign key column name 
        if model_table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_table_name][0][1]
            
        return self_fkey


    # def __get_foreign_key_from_instance(self, model_instance):
    #     self_fkey = f'{model_instance.__class__.__name__.lower()}_id'

    #     if model_instance.table_name in self.FOREIGN_KEY_MAP:
    #         self_fkey = self.FOREIGN_KEY_MAP[model_instance.table_name][0][1]

    #     return self_fkey


    def __get_pivot_name(self, model) -> str:
        """Returns the pivot table between `self` and the given LiteModel instance or class, if it exists.

        Args:
            model (LiteModel): LiteModel class or instance

        Returns:
            str: Name of pivot table
        """

        # Derive conventional naming scheme for pivot tables
        model_names = []
        model_names.append(self.__class__.__name__.lower())

        try: model_name = getattr(model, '__name__').lower()
        except: model_name = model.__class__.__name__.lower()
        model_names.append(model_name)

        model_names = sorted(model_names) # Make alphabetical
        pivot_table_name = '_'.join(model_names) # Join into string of format 'model_model'

        # Check to see if table with this name exists
        if LiteTable.is_pivot_table(pivot_table_name):
            return pivot_table_name # If it does, return the table name


    def __init__(self,id:int=None):
        """LiteModel initializer.

        Args:
            id (int, optional): The id of the model instance within the database. Defaults to None, which does not load from database.
        """

        # Get database path
        self.database_path = Lite.get_database_path()

        # Derive table name from class name
        self.table_name = self.__get_table_name()
        self.table = LiteTable(self.table_name)

        # Generate dict map of foreign key references. Used by .__get_foreign_key_from_model()
        self.FOREIGN_KEY_MAP = self.table.get_foreign_key_references()

        # Load model instance from database if an id is provided
        if id is not None:

            try:
                columns = self.table.execute_and_fetch(f'PRAGMA table_info({self.table_name})')
                values = self.table.select([['id','=',id]])
            except: 
                raise ModelInstanceNotFoundError(id)

            # Add columns and values to python class instance as attributes
            for i in range(0,len(columns)):
                try: value = values[0][i]
                except: value = None
                setattr(self, columns[i][1], value)
                
            # Store list of all table column names. Used by .save()
            self.table_columns = [column[1] for column in columns]


    def __get_relationship_methods(self) -> list:
        """Returns a list of method names that define model-model relationships.

        To ensure methods are correctly identified as relationship definitions,
        make sure to specify a return type of `LiteCollection` or `LiteModel` when
        defining them.

        Returns:
            list: A list of method names as strings
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


    @classmethod
    def findOrFail(self, id:int):
        """Returns a LiteModel instance with id matching the passed value. Throws an exception if an instance isn't found.

        Args:
            id (int): _description_

        Raises:
            ModelInstanceNotFoundError: _description_

        Returns:
            _type_: _description_
        """
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(table_name)
        rows = table.select([['id','=',id]])

        if len(rows) > 0:
            return self(id) # Return LiteModel
        else:
            raise ModelInstanceNotFoundError(id)

    @classmethod
    def find(self, id):
        """Returns LiteModel with matching id or None."""
        try:
            return self.findOrFail(id)
        except ModelInstanceNotFoundError:
            return None

    @classmethod
    def all(self):
        """Returns a list of all LiteModels in database."""
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(table_name)

        collection = []
        rows = table.select([],['id'])
        for row in rows:
            collection.append(self.findOrFail(row[0]))
        
        return LiteCollection(collection)

    @classmethod
    def where(self, where_columns):
        """Returns a list of LiteModels matching query from database."""

        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(table_name)

        collection = []
        rows = table.select(where_columns,['id'])
        for row in rows:
            collection.append(self.findOrFail(row[0]))
        
        return LiteCollection(collection)

    @classmethod
    def create(self,column_values):
        """Creates a new table."""
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(table_name)

        table.insert(column_values)

        sql_str = f'SELECT id FROM {table_name} WHERE {list(column_values.keys())[0]} = ? ORDER BY id DESC'
        ids = table.execute_and_fetch(
            sql_str,
            tuple([column_values[list(column_values.keys())[0]]])
        )
        if len(ids) > 0:
            return self(ids[0][0])
        else:
            raise Exception('Could not locate model that was created.')

    @classmethod
    def createMany(self,column_list:list):
        """Creates multiple new entries in the database."""
        
        model_list = []
        for column_set in column_list:
            model_list.append(self.create(column_set))
        
        return model_list

    def attach(self, model_instance, self_fkey=None, model_fkey=None):
        
        try: pivot_table_name = self.__get_pivot_name(model_instance)
        except: pivot_table_name = False

        # print("PIVOT TABLE NAME", pivot_table_name)
        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name)

            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            # user should provide a self and model foreign keys if the pivot table associates two rows from the *same* table
            if not self_fkey or not model_fkey:
                if model_instance.table_name == self.table_name and len(foreign_keys[self.table_name]) > 1:
                    self_fkey = foreign_keys[self.table_name][0][1]
                    model_fkey = foreign_keys[model_instance.table_name][1][1]
                else:
                    self_fkey = foreign_keys[self.table_name][0][1]
                    model_fkey = foreign_keys[model_instance.table_name][0][1]

            # Make sure this relationship doesn't already exist
            relationships = pivot_table.select([
                [self_fkey,'=',self.id],
                [model_fkey,'=',model_instance.id]
            ])

            if len(relationships) == 0:
                pivot_table.insert({
                    self_fkey: self.id,
                    model_fkey: model_instance.id
                })
                # print(Fore.GREEN, "Attached models via pivot table.", Fore.RESET)
            else:
                raise RelationshipError(f"This relationship already exists.")

            return True
            
        else:

            # Derive foreign keys
            self_fkey = model_instance.__get_foreign_key_from_model(self)
            model_fkey = self.__get_foreign_key_from_model(model_instance)

            if self.__has_column(model_fkey):
                if getattr(self, model_fkey) == None:
                    setattr(self, model_fkey, model_instance.id)
                    self.save()
                else:
                    raise RelationshipError(f"There is a pre-existing relationship. Remove it with .detach() before proceeding.")
            else:
                if getattr(model_instance, self_fkey) == None:
                    setattr(model_instance, self_fkey, self.id)
                    model_instance.save()
                else:
                    raise RelationshipError(f"There is a pre-existing relationship. Remove it with .detach() before proceeding.")

        # print(Fore.GREEN, "Attached models", Fore.RESET)
        return True

    def attachMany(self, model_instances, local_key:str='id'):
        for model_instance in model_instances:
            self.attach(model_instance)

    def detach(self, model_instance, local_key:str='id'):
        
        try: pivot_table_name = self.__get_pivot_name(model_instance)
        except: pivot_table_name = False

        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(pivot_table_name)
            
            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            if model_instance.table_name == self.table_name and len(foreign_keys[self.table_name]) > 1:
                self_fkey = foreign_keys[self.table_name][0][1]
                model_fkey = foreign_keys[model_instance.table_name][1][1]
            else:
                self_fkey = foreign_keys[self.table_name][0][1]
                model_fkey = foreign_keys[model_instance.table_name][0][1]

            # Make sure this relationship doesn't already exist
            relationships = pivot_table.delete([
                [self_fkey,'=',self.id],
                [model_fkey,'=',model_instance.id]
            ])
        else:
            # Derive foreign keys
            self_fkey = model_instance.__get_foreign_key_from_model(self)
            model_fkey = self.__get_foreign_key_from_model(model_instance)

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

    def detachMany(self, model_instances, local_key:str='id'):
        for model_instance in model_instances:
            self.detach(model_instance)

    def __clean_attachments(self):
        foreign_keys = self.table.get_foreign_key_references()
        table_names = self.table.get_all_table_names()

        check_tables = {}

        for t_name in table_names:
            temp_table = LiteTable(t_name)

            temp_foreign_keys = temp_table.get_foreign_key_references()

            if self.table.table_name in temp_foreign_keys:
                check_tables[temp_table.table_name] = temp_foreign_keys[self.table.table_name]

        for tName in check_tables:
            # Get local and foreign keys
            key_maps = check_tables[tName]
            for i in range(0, len(key_maps)):
                local_key = key_maps[i][0]
                foreign_key = key_maps[i][1]

                local_key_value = getattr(self, local_key)

                # Check if table is a pivot table, as detach proceedure will be different
                temp_table = LiteTable(tName)
                if LiteTable.is_pivot_table(tName):
                    # print(Back.BLUE, "Deleting from pivot table", local_key_value, Back.RESET)
                    temp_table.delete([[foreign_key,'=',local_key_value]])
                else:
                    # Update table to remove reference to self model instance
                    temp_table.update({foreign_key: None}, [[foreign_key,'=',local_key_value]],True)
                

    def delete(self):
        if self.id == None: raise ModelInstanceNotFoundError(self.id) # cannot delete a model instance that isn't saved in database

        self.__clean_attachments() # remove any attachments that would otherwise stick around after deleting the model instance

        self.table.delete([['id','=',self.id]])

        # Since the python object instance cannot be removed from memory manually,
        # set all attributes to None
        for column in self.table_columns: setattr(self, column, None)

        return True
        

    def save(self):
        update_columns = {}
        for column in self.table_columns:
            if column == 'id': continue # don't update or insert id directly
            update_columns[column] = getattr(self, column)

        if self.id == None: # Create model if no ID is provided
            self.table.insert(update_columns)
        else:
            self.table.update(update_columns,[['id','=',self.id]])

    def belongsTo(self, model, foreign_key=None, local_key=None):

        # Derive foreign and local keys if none are provided
        if not foreign_key: foreign_key = self.__get_foreign_key_from_model(model)
        # if not local_key: local_key = "id"

        # Get database row ID of parent model
        parent_model_id = getattr(self, foreign_key)

        return model.find(parent_model_id)

    def belongsToMany(self, model): # Many-to-many

        # Check to see if pivot table exists - - -
        # First, check pivot table cache for this model
        model_class_name = getattr(model, '__name__').lower()
        if model_class_name not in self.PIVOT_TABLE_CACHE:
            pivot_table_name = self.__get_pivot_name(model)
            pivot_table = LiteTable(pivot_table_name)

            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            self.PIVOT_TABLE_CACHE[model_class_name] = [pivot_table_name, foreign_keys]     
        else: # If the pivot table for this relationship is already in the cache, use it
            pivot_table_name, foreign_keys = self.PIVOT_TABLE_CACHE[model_class_name]

        model_instance = model()

        # Handles pivot tables that relate two of the same model
        if model_instance.table_name == self.table_name and len(foreign_keys[self.table_name]) > 1:
            self_fkey = [foreign_keys[self.table_name][0][1],foreign_keys[self.table_name][1][1]]
            model_fkey = [foreign_keys[model_instance.table_name][1][1],foreign_keys[model_instance.table_name][0][1]]
        else:
            self_fkey = foreign_keys[self.table_name][0][1]
            model_fkey = foreign_keys[model_instance.table_name][0][1]

        # Assume relationship is many-to-many
        siblings_collection = []
        relationships = []

        if type(self_fkey) == list:
            select_queries = []
            for i in range(0, len(self_fkey)):
                select_queries.append(f'SELECT {model_fkey[i]} FROM {pivot_table_name} WHERE {self_fkey[i]} = {self.id}')
            relationships = self.table.execute_and_fetch(' UNION '.join(select_queries))
        else:
            relationships = self.table.execute_and_fetch(f'SELECT {model_fkey} FROM {pivot_table_name} WHERE {self_fkey} = {self.id}')

        for rel in relationships:
            try: 
                sibling = model.find(rel[0])
            except ModelInstanceNotFoundError: 
                print("Error occurred!")
                continue
            siblings_collection.append(sibling)

        return LiteCollection(siblings_collection)

    def hasOne(self, model, foreign_key=None, local_key=None): # One-to-one
        child_table_name = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_model(self)

        child_table = LiteTable(child_table_name)
        child_ids = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])
        
        if len(child_ids) > 0:
            return model.find(child_ids[0][0])
        else:
            return None


    def hasMany(self, model, foreign_key=None, local_key=None): # One-to-many

        child_table_name = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        model_instance = model()
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_model(self)
        
        child_table = LiteTable(child_table_name)
        child_rows = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])

        children_collection = []
        for row in child_rows:
            children_collection.append(model(row[0]))

        return LiteCollection(children_collection)


    def findPath(self, to_model_instance, max_depth:int=100, shortestPath:bool = True):

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
        return False

    def __findPath__iteration(self, open_nodes, closed_nodes, to_model_instance):

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


        

