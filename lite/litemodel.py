import re # used for pluralizing class names to derive table name
from lite.litetable import LiteTable
from lite.liteexceptions import *
from lite.lite import Lite

class LiteCollection:

    def __init__(self, list):
        self.list = list

    def __str__(self):
        return self.list.__str__()

    def __len__(self):
        return len(self.list)

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

    def __get_foreign_key_references(self):
        self.table.cursor.execute(f'PRAGMA foreign_key_list({self.table_name})')
        foreign_keys = self.table.cursor.fetchall()

        foreign_key_map = {}

        for fkey in foreign_keys:
            table_name = fkey[2]
            foreign_key = fkey[3]
            local_key = fkey[4]

            if table_name not in foreign_key_map: foreign_key_map[table_name] = {}

            foreign_key_map[table_name][local_key] = foreign_key
            
        return foreign_key_map

    def __get_foreign_key_from_model(self, model, local_key:str='id'):
        self_fkey = f'{model.__name__.lower()}_id'
        model_table_name = self.__pluralize(model.__name__.lower())
        if model_table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_table_name][local_key]

        return self_fkey

    def __get_foreign_key_from_instance(self, model_instance, local_key:str='id'):
        self_fkey = f'{model_instance.__class__.__name__.lower()}_id'
        if model_instance.table_name in self.FOREIGN_KEY_MAP:
            self_fkey = self.FOREIGN_KEY_MAP[model_instance.table_name][local_key]

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
        self.table = LiteTable(self.database_path, self.table_name)
        self.FOREIGN_KEY_MAP = self.__get_foreign_key_references()

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

    @classmethod
    def findOrFail(self, id):
        """Returns LiteModel with matching id."""
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(database_path, table_name)
        rows = table.select([['id','=',id]])

        if len(rows) > 0:
            return self(id) # Return LiteModel
        else:
            raise ModelNotFoundError(id)

    @classmethod
    def all(self):
        """Returns a list of all LiteModels in database."""
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(database_path, table_name)

        collection = []
        rows = table.select([],['id'])
        for row in rows:
            collection.append(self.findOrFail(row[0]))
        
        return LiteCollection(collection)

    @classmethod
    def create(self,column_values):
        """Creates a new table."""
        
        database_path = Lite.get_database_path()
        table_name = self.__pluralize(self,self.__name__.lower())
        
        table = LiteTable(database_path, table_name)

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

    def attach(self, model_instance, local_key:str='id'):
        
        pivot_table_name = self.__pivot_table_exists(model_instance)
        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(Lite.get_database_path(),pivot_table_name)

            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            self_fkey = foreign_keys[self.table_name]['id']
            model_fkey = foreign_keys[model_instance.table_name]['id']

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
                print(Fore.GREEN, "Attached models via pivot table.", Fore.RESET)
            else:
                print(Fore.GREEN, "This relationship already exists in pivot table.", Fore.RESET)

            return True
            
        else:

            # Derive foreign keys
            self_fkey = model_instance.__get_foreign_key_from_instance(self)
            model_fkey = self.__get_foreign_key_from_instance(model_instance)

            if self.__has_column(model_fkey):
                setattr(self, model_fkey, model_instance.id)
                self.save()
            else:
                print("Setting", self_fkey, "on", model_instance.table_name)
                setattr(model_instance, self_fkey, self.id)
                
                model_instance.save()

        # elif model_a_fkey in model_b_cols:
        #     setattr(model_instance, model_a_fkey, self.id)
        #     model_instance.save()

        print(Fore.GREEN, "Attached models", Fore.RESET)
        return True

    def detach(self, model_instance, local_key:str='id'):
        
        pivot_table_name = self.__pivot_table_exists(model_instance)
        if pivot_table_name: # Is a many-to-many relationship
            pivot_table = LiteTable(Lite.get_database_path(),pivot_table_name)
            
            # Derive foreign keys
            foreign_keys = pivot_table.get_foreign_key_references()

            self_fkey = foreign_keys[self.table_name]['id']
            model_fkey = foreign_keys[model_instance.table_name]['id']

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
                setattr(self, model_fkey, None)
                self.save()
            else:
                setattr(model_instance, self_fkey, None)
                model_instance.save()

        print("Detached models")

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

        return model.findOrFail(parent_model_id)

    def belongsToMany(self, model): # Many-to-many

        # Check to see if pivot table exists - - -
        pivot_table_name = self.__pivot_table_exists(model)
        pivot_table = LiteTable(self.database_path, pivot_table_name)

        # Derive foreign keys
        model_instance = model()
        foreign_keys = pivot_table.get_foreign_key_references()

        self_fkey = foreign_keys[self.table_name]['id']
        model_fkey = foreign_keys[model_instance.table_name]['id']

        # Assume relationship is many-to-many
        self.table.cursor.execute(f'SELECT {model_fkey} FROM {pivot_table_name} WHERE {self_fkey} = {self.id}')
        relationships = self.table.cursor.fetchall()

        siblings_collection = []
        for rel in relationships:
            try: 
                sibling = model.findOrFail(rel[0])
            except ModelNotFoundError: 
                print("Error occured!")
                continue
            siblings_collection.append(sibling)

        return LiteCollection(siblings_collection)

    def hasOne(self, model, foreign_key=None, local_key=None): # One-to-one

        child_table_name = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        if not foreign_key: foreign_key = self.__get_foreign_key_from_instance(self)
        # if not local_key: local_key = f'{model.__name__.lower()}_id'

        print("Has one", foreign_key)

        child_table = LiteTable(self.database_path, child_table_name)
        child_ids = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])
        
        if len(child_ids) > 0:
            return model.findOrFail(child_ids[0][0])
        else:
            return None

    def hasMany(self, model, foreign_key=None, local_key=None): # One-to-many

        child_table_name = self.__pluralize(model.__name__.lower())

        # Derive foreign and local keys if none are provided
        if not foreign_key: foreign_key = f'{self.__class__.__name__.lower()}_id'
        # if not local_key: local_key = f'{model.__name__.lower()}_id'

        
        child_table = LiteTable(self.database_path, child_table_name)
        child_rows = child_table.select([
            [foreign_key,'=',self.id]
        ],['id'])

        children_collection = []
        for row in child_rows:
            children_collection.append(model(row[0]))

        return LiteCollection(children_collection)