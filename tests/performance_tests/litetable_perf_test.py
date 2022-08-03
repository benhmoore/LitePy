import os, time, random, string
from lite import *


test_db = 'perf.sqlite'

os.environ['DB_DATABASE'] = test_db
try: os.remove(test_db)
except: pass

Lite.createDatabase(test_db)
testingTable = LiteTable.createTable('test_table',{
    'key': 'blob',
    'value': 'blob'
})

def generate_random_string(def_len=20):
    # printing lowercase
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(def_len))

# Generate 100,000 test key/value pairs
number = 10000
keys = [generate_random_string(30) for i in range(0, number)]
values = [generate_random_string(30) for i in range(0, number)]

# Test create 1,000 tables
def test_tables():

    names = [generate_random_string() for i in range(0, 500)]

    # Test table creation

    start = time.perf_counter()

    for i in range(0,len(names)):
        LiteTable.createTable(names[i], {
            'test_field': 'INTEGER'
        })

    print("Time to create 2,000 tables: ", time.perf_counter() - start, "seconds")

    # time.sleep(5)

    # Test table deletion

    start = time.perf_counter()


    for i in range(0,500):
        LiteTable.deleteTable(names[i])

    print("Time to delete 2,000 tables: ", time.perf_counter() - start, "seconds")

def test_inserts():
    
    start = time.perf_counter()

    for i in range(0,len(keys)):
        testingTable.insert({
            'key': keys[i],
            'value': values[i]
        })

    print(f"Time to insert {len(keys)} rows: ", time.perf_counter() - start, "seconds")

def test_updates():

    start = time.perf_counter()

    for i in range(0, len(keys)):
        testingTable.update({
            'value': -1
        }, [
            ['key','=',keys[i]]
        ])

    print(f"Time to update {len(keys)} rows: ", time.perf_counter() - start, "seconds")

def test_select():

    start = time.perf_counter()

    results = testingTable.select([['key','LIKE','%xy%']])

    print(f"Time to select from {len(keys)} rows: ", time.perf_counter() - start, "seconds")


def test_deletes():

    start = time.perf_counter()

    for i in range(0, len(keys)):
        testingTable.delete([
            ['key','=',keys[i]]
        ])

    print(f"Time to delete {len(keys)} rows: ", time.perf_counter() - start, "seconds")
    

def run_tests():
    test_tables()
    test_inserts()
    test_updates()
    test_select()
    test_deletes()

run_tests()