import re, typing, queue # used for pluralizing class names to derive table name
from lite.litetable import LiteTable
from lite.liteexceptions import *
from lite.lite import Lite

#
# From https://www.geeksforgeeks.org/priority-queue-in-python/
# A simple implementation of Priority Queue
# using Queue.
#

class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)
    
    def __str__(self):
        return str(self.queue)
  
    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0
  
    # for inserting an element in the queue
    def insert(self, node):
        self.queue.append(node)

    def containsPosition(self, node):
        nodes = []
        for q_node in self.queue:
            if q_node.pos == node.pos:
                nodes.append(q_node)
        
        if len(nodes) < 1: return False

        try:
            min = 0
            for i in range(len(nodes)):
                if nodes[i].f < nodes[min].f:
                    min = i
            item = nodes[min]
            del nodes[min]
            return item
        except IndexError:
            print()
            exit()
  
    def popMin(self):
        cumulative_g = 0
        
        try:
            min = 0
            for i in range(len(self.queue)):
                if self.queue[i].f < self.queue[min].f:
                    min = i
            item = self.queue[min]
            del self.queue[min]
            return item
        except IndexError:
            print()
            exit()

class LiteCollection:

    def __init__(self, model_instances:list=None):
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

    def add(self, model_instance):
        """Adds a model instance to the collection."""

        accepted = True
        for m_inst in self.list:
            if m_inst == model_instance:
                accepted = False
        
        if accepted:
            self.list.append(model_instance)
        else:
            raise DuplicateModelInstance(model_instance)

    def join(self, lite_collection):
        """Merges a LiteCollection into the current one."""
        
        self.list += lite_collection.list


    def remove(self, model_instance):
        """Removes a model instance from the collection."""

        try: self.list.remove(model_instance)
        except: raise ModelInstanceNotFoundError(model_instance.id)


    def __getitem__(self, item):
        return self.list[item]

    def where(self, where_columns):
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
    """Model-based system for database management. Inspired by Laravel."""


    def toDict(self):
        """Converts the LiteModel into a human-readable dictionary, with truncated values where necessary."""
        print_dict = {}
        for column in self.table_columns:
            attribute = getattr(self, column)

            # Convert byte strings to regular strings
            if type(attribute) == bytes: attribute = attribute.decode("utf-8") 

            # Truncate text over 50 characters)
            if type(attribute) == str: attribute = attribute[:50] + '...'
            print_dict[column] = attribute

        return print_dict

    def __str__(self):
        return self.toDict().__str__()

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

    def __pluralize(self, noun):
        if re.search('[sxz]$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('[^aeioudgkprt]h$', noun):
            return re.sub('$', 'es', noun)
        elif re.search('[aeiou]y$', noun):
            return re.sub('y$', 'ies', noun)
        else:
            return noun + 's'

    def __get_table_name(self):
        return self.__pluralize(self.__class__.__name__.lower())

    def __has_column(self, column_name):
        if column_name in self.table_columns:
            return True
        else:
            return False

    def get_foreign_key_references(self):
        self.table.cursor.execute(f'PRAGMA foreign_key_list({self.table_name})')
        foreign_keys = self.table.cursor.fetchall()

        foreign_key_map = {}

        for fkey in foreign_keys:
            table_name = fkey[2]
            foreign_key = fkey[3]
            local_key = fkey[4]

            if table_name not in foreign_key_map: foreign_key_map[table_name] = []

            foreign_key_map[table_name].append([local_key, foreign_key])
            
        return foreign_key_map

    def __get_foreign_key_from_model(self, model, local_key:str='id'):
        self_fkey = f'{model.__name__.lower()}_id'
        model_table_name = self.__pluralize(model.__name__.lower())
        if model_table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_table_name][0][1]
            
        return self_fkey

    def __get_foreign_key_from_instance(self, model_instance, local_key:str='id'):
        self_fkey = f'{model_instance.__class__.__name__.lower()}_id'

        if model_instance.table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_instance.table_name][0][1]

        return self_fkey

    def __pivot_table_exists(self, model):
        # Check to see if pivot table exists - - -
        # Derive pivot table name from conventions
        model_names = []
        model_names.append(self.__class__.__name__.lower())

        try:
            model_name = getattr(model, '__name__').lower()
        except: model_name = model.__class__.__name__.lower()
        model_names.append(model_name)

        model_names = sorted(model_names)
        pivot_table_name = '_'.join(model_names)

        # Check to see if pivot table exists
        self.table.cursor.execute(f'PRAGMA table_info({pivot_table_name})')
        if len(self.table.cursor.fetchall()) > 0:
            return pivot_table_name
        else:
            return False

    def __init__(self,id=None):

        # Get database path from .env file
        self.database_path = Lite.get_database_path()

        # Derive table name from class name
        self.table_name = self.__get_table_name()
        self.table = LiteTable(self.table_name)
        self.FOREIGN_KEY_MAP = self.get_foreign_key_references()

        if id is not None:

            # Load columns and values from database for this model
            self.table.cursor.execute(f'PRAGMA table_info({self.table_name})')
            
            columns = self.table.cursor.fetchall()
            values = self.table.select([['id','=',id]])

            for i in range(0,len(columns)):
                value = None
                try:
                    value = values[0][i]
                except Exception: pass

                setattr(self, columns[i][1], value)
                
            # Store list of all table column names. This is used for save()
            self.table_columns = [column[1] for column in columns]

    def __get_relationship_methods(self):
        """Returns a list of method names that should define relationships between model instances."""

        # First, find all unique methods for the current model instance
        instance_variables = set(filter(lambda x: x.startswith('_') == False, dir(self)))
        default_variables = set(filter(lambda x: x.startswith('_') == False, dir(LiteModel)))

        unique_variables = instance_variables - default_variables
        unique_methods = []

        for i_var in unique_variables:
            try: 
                getattr(getattr(self, i_var), '__call__')
                unique_methods.append(i_var)
            except: continue
                

        # These unique methods should contain any relationship definitions (i.e. calling hasOne, hasMany, belongsToMany, etc.)
        # To find these relationship definitions, we look for methods that return either a LiteCollection or LiteModel:

        relationship_definitions = []
        for method in unique_methods:
            method_signature = typing.get_type_hints(getattr(self, method))

            if "return" in method_signature:
                if method_signature['return'] == LiteCollection or method_signature['return'] == LiteModel:
                    relationship_definitions.append(method)

        return relationship_definitions


    @classmethod
    def findOrFail(self, id):
        """Returns LiteModel with matching id or throws exception."""
        
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
        table.cursor.execute(
            sql_str,
            tuple([column_values[list(column_values.keys())[0]]])
        )
        ids = table.cursor.fetchall()
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
        
        pivot_table_name = self.__pivot_table_exists(model_instance)
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
            self_fkey = model_instance.__get_foreign_key_from_instance(self)
            model_fkey = self.__get_foreign_key_from_instance(model_instance)

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
        
        pivot_table_name = self.__pivot_table_exists(model_instance)
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
            self_fkey = model_instance.__get_foreign_key_from_instance(self)
            model_fkey = self.__get_foreign_key_from_instance(model_instance)

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
        foreign_keys = self.get_foreign_key_references()
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
        pivot_table_name = self.__pivot_table_exists(model)
        pivot_table = LiteTable(pivot_table_name)

        # Derive foreign keys
        model_instance = model()
        foreign_keys = pivot_table.get_foreign_key_references()

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
            for i in range(0, len(self_fkey)):
                self.table.cursor.execute(f'SELECT {model_fkey[i]} FROM {pivot_table_name} WHERE {self_fkey[i]} = {self.id}')
                relationships.append(self.table.cursor.fetchall())

        else:

            self.table.cursor.execute(f'SELECT {model_fkey} FROM {pivot_table_name} WHERE {self_fkey} = {self.id}')
            relationships.append(self.table.cursor.fetchall())

        for rel_set in relationships:
            for rel in rel_set:
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
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_instance(self)

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
        if not foreign_key: foreign_key = model_instance.__get_foreign_key_from_instance(self)
        
        child_table = LiteTable(child_table_name)
        child_rows = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])

        children_collection = []
        for row in child_rows:
            children_collection.append(model(row[0]))

        return LiteCollection(children_collection)

    def findPath(self, to_model_instance, max_depth:int=20, _path:list=None, _explored:list=None):
        """Attempts to find a path to the model using BFS."""

        if to_model_instance == self: # Don't attempt to find a path to self
            return LiteCollection([])

        if not _path: _path = []
        if not _explored: _explored = []

        _path.append(self)
        if len(_path) > max_depth:
            print("Reached max depth!")
            return False

        # Get relationship definition methods
        rel_methods = self.__get_relationship_methods()

        rel_results = LiteCollection()
        
        for method in rel_methods:
            result = getattr(self, method)()
            if result:
                if type(result) == LiteCollection:
                    try: rel_results.join(result)
                    except: pass
                else:
                    try: rel_results.add(result)
                    except: pass

        print(Back.RED,rel_results,Back.RESET)
        print(Back.BLUE,LiteCollection(_explored),Back.BLUE)

        if to_model_instance in rel_results:
            _path.append(to_model_instance)
            return LiteCollection(_path)

        _explored.append(self)
        
        for result_model in rel_results:
            # if result_model: 
            if result_model != self:
                if result_model not in _explored:
                    return result_model.findPath(to_model_instance, max_depth, _path, _explored)

        return False   

        

