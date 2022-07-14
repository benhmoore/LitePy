import os, time, hashlib
from lite import *

class Lite:

    FETCH_CACHE = {}
    DATABASE_FILE_HASH = None

    @staticmethod
    def hash_file(filepath):
        sha1 = hashlib.sha1()
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    @staticmethod
    def get_env():
        env_dict = {}
        if os.path.exists('.env'):
            with open('.env') as env:
                for line in env:
                    key, value = line.split('=')
                    env_dict[key] = value
            return env_dict
        else:
            raise EnvFileNotFound()
    
    @staticmethod
    def get_database_path():
        db_path = os.environ.get('DB_DATABASE')
        if db_path is not None: # Look for database path in environment variables first
            return db_path
        else: # Otherwise, pull from .env file
            env = Lite.get_env()
            if 'DB_DATABASE' in env:
                return env['DB_DATABASE']
            else:
                raise DatabaseNotFoundError('')

    @classmethod
    def clean_fetch_cache(self, table_name, sql_str, cutoff_time:float=10.0):
        if table_name not in self.FETCH_CACHE: self.FETCH_CACHE[table_name] = {}
        if sql_str not in self.FETCH_CACHE[table_name]: self.FETCH_CACHE[table_name][sql_str] = []

        delete_indexes = []
        for i in range(0, len(self.FETCH_CACHE[table_name][sql_str])):
            if time.perf_counter() - self.FETCH_CACHE[table_name][sql_str][i][2] > cutoff_time:
                delete_indexes.append(i)
        
        for index in sorted(delete_indexes, reverse=True):
            del self.FETCH_CACHE[table_name][sql_str][index]


    @classmethod
    def add_fetch_cache(self, table_name, sql_str, values, results):
        if table_name not in self.FETCH_CACHE: self.FETCH_CACHE[table_name] = {}
        if sql_str not in self.FETCH_CACHE[table_name]: self.FETCH_CACHE[table_name][sql_str] = []

        self.FETCH_CACHE[table_name][sql_str].append([values, results, time.perf_counter()])


    @classmethod
    def get_fetch_cache(self, table_name, sql_str, values):
        new_hash = Lite.hash_file(Lite.get_database_path())
        if new_hash != self.DATABASE_FILE_HASH:
            print("Hash not the same. Pulling from database.")
            self.DATABASE_FILE_HASH = new_hash
            return False

        if table_name not in self.FETCH_CACHE: self.FETCH_CACHE[table_name] = {}
        if sql_str not in self.FETCH_CACHE[table_name]: self.FETCH_CACHE[table_name][sql_str] = []

        for query in self.FETCH_CACHE[table_name][sql_str]:
            if query[0] == values:
                # pprint.pprint(self.FETCH_CACHE)
                return query[1]
                

        return False