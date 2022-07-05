import pytest, sqlite3, os
from lite.litemodel import LiteModel
from lite.litetable import LiteTable


# Setup database
test_db = 'tests_database.db'
try:
    os.remove('tests_database.db')
except Exception: pass

LiteTable.create_database(test_db)

# Test LiteTable Module - - - - - - -
@pytest.mark.parametrize("table_name,expected", [
    ('table_a', True),
    ('table_b', True),
])
def test_create_tables(table_name, expected):
    assert LiteTable.create_table(test_db, table_name, {'name':'TEXT'}) == expected

@pytest.mark.parametrize("table_name,expected", [
    ('table_b', True),
])
def test_delete_tables(table_name, expected):
    assert LiteTable.delete_table(test_db, table_name) == expected

# .delete_table() should only remove a table if it exists.
# It should not raise an exception
def test_delete_nonexistant_table():
    assert LiteTable.delete_table(test_db, 'table_b') == True

# Test .exists()
@pytest.mark.parametrize("table_name,expected", [
    ('table_a', True),
    ('table_b', False),
])
def test_exists(table_name, expected):
    assert LiteTable.exists(test_db, table_name) == expected

# Test .create_database()
def test_create_database():
    assert LiteTable.create_database(test_db) == True

# Test .insert()
@pytest.mark.parametrize("columns, expected", [
    ({'name':'testing123'}, True),
    ({'name':'321'}, True),
    ({'name':'apple'}, True),
])
def test_insert(columns, expected):
    table = LiteTable(test_db, 'table_a')
    assert table.insert(columns) == True

# Test .update()
def test_update():
    table = LiteTable(test_db, 'table_a')
    assert table.update({'name':'testing987'},[['id','=',1]]) == True

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
    table = LiteTable(test_db, 'table_a')
    assert len(table.select(where_columns)) == expected

# Test .delete()
@pytest.mark.parametrize("where_columns, expected", [
    ([['name','LIKE','%321%']], 2),
    ([['name','=','orange']], 2),
])
def test_delete(where_columns, expected):
    table = LiteTable(test_db, 'table_a')
    table.delete(where_columns)
    assert len(table.select([])) == expected
