import pytest, sqlite3, os
from lite.liteexceptions import DatabaseAlreadyExists
from lite.litemodel import LiteModel
from lite.litetable import LiteTable

os.environ['DB_DATABASE'] = 'pytest.db'

# Setup database
test_db = 'pytest.db'
try: os.remove('pytest.db')
except: pass

LiteTable.create_database(test_db)

# Test LiteTable Module - - - - - - -

# Test .create_database()
def test_create_database():
    try: LiteTable.create_database(test_db)
    except DatabaseAlreadyExists: pass
    
@pytest.mark.parametrize("table_name,expected", [
    ('table_a', True),
    ('table_b', True),
])
def test_create_tables(table_name, expected):
    LiteTable.create_table(table_name, {'name':'TEXT'})

@pytest.mark.parametrize("table_name,expected", [
    ('table_b', True),
])
def test_delete_tables(table_name, expected):
    LiteTable.delete_table(table_name)

# .delete_table() should only remove a table if it exists.
# It should not raise an exception
def test_delete_nonexistant_table():
    LiteTable.delete_table('table_b')

# Test .exists()
@pytest.mark.parametrize("table_name,expected", [
    ('table_a', True),
    ('table_b', False),
])
def test_exists(table_name, expected):
    assert LiteTable.exists(table_name) == expected

# Test .insert()
@pytest.mark.parametrize("columns, expected", [
    ({'name':'testing123'}, True),
    ({'name':'321'}, True),
    ({'name':'apple'}, True),
])
def test_insert(columns, expected):
    table = LiteTable('table_a')
    table.insert(columns)

# Test .update()
def test_update():
    table = LiteTable('table_a')
    table.update({'name':'testing987'},[['id','=',1]])

# Test .select()
@pytest.mark.parametrize("where_columns, expected", [
    ([['name','LIKE','%987%']], 1),
    ([['name','=','testing987']], 1),
    ([['name','= NOT','xyz']], 0),
    ([['name','= NOT','testing87']], 0),
    ([['id','=','1']], 1),
    # ('table_b', False),
])
def test_select(where_columns, expected):
    table = LiteTable('table_a')
    assert len(table.select(where_columns)) == expected

# Test .delete()
@pytest.mark.parametrize("where_columns, expected", [
    ([['name','LIKE','%321%']], 2),
    ([['name','=','orange']], 2),
])
def test_delete(where_columns, expected):
    table = LiteTable('table_a')
    table.delete(where_columns)
    assert len(table.select([])) == expected
