<!-- markdownlint-disable -->

<a href="../pylite/lite_table.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_table`
Contains the LiteTable class  



---

<a href="../pylite/lite_table.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LiteTable`
Facilitates common table operations on an SQLite database. 



**Raises:**
 
 - <b>`DatabaseAlreadyExists`</b>:  Database already exists at filepath 
 - <b>`DatabaseNotFoundError`</b>:  Database not specified by environment file or variables. 
 - <b>`TableNotFoundError`</b>:  Table not found within database 

<a href="../pylite/lite_table.py#L387"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(table_name: str, lite_connection: LiteConnection = None)
```

LiteTable initializer. 



**Args:**
 
 - <b>`table_name`</b> (str):  Name of table within database to connect to disable_isolation (bool, optional):  Determines whether the SQLite connection disables isolation. Defaults to False. disable_WAL (bool, optional):  Determines whether the SQLite connection disables wal. Defaults to False. 



**Raises:**
 
 - <b>`DatabaseNotFoundError`</b>:  Database not found 
 - <b>`InvalidDatabaseError`</b>:  Database isn't a valid Lite database 
 - <b>`TableNotFoundError`</b>:  Table not found within database 




---

<a href="../pylite/lite_table.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_table`

```python
create_table(
    table_name: str,
    columns: dict,
    foreign_keys: dict = None,
    lite_connection: LiteConnection = None
)
```

Creates a table within the database. 



**Args:**
 
 - <b>`table_name`</b> (str):  Table name 
 - <b>`columns`</b> (dict):  { 
 - <b>`column_name`</b>:  field_attributes } 
 - <b>`foreign_keys`</b> (dict, optional):  { 
 - <b>`column_name`</b>:  [foreign_table_name, foreign_column_name] } 

---

<a href="../pylite/lite_table.py#L320"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete`

```python
delete(where_columns: list = None)
```

Deletes rows from a database table. If where_columns is an empty list, deletes all rows. 



**Args:**
 
 - <b>`where_columns`</b> (list):  [  [column_name, ('=','<','>','LIKE'), column_value] ] 

---

<a href="../pylite/lite_table.py#L191"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_table`

```python
delete_table(table_name: str, lite_connection: LiteConnection = None)
```

Deletes a given table. 



**Args:**
 
 - <b>`table_name`</b> (str):  Table name 

---

<a href="../pylite/lite_table.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `exists`

```python
exists(table_name: str, lite_connection: LiteConnection = None) → bool
```

Checks if table exists in database. 



**Args:**
 
 - <b>`table_name`</b> (str):  Table name 



**Returns:**
 bool 

---

<a href="../pylite/lite_table.py#L224"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_column_names`

```python
get_column_names() → list
```

Returns a list of the table's column names. 



**Returns:**
 
 - <b>`list`</b>:  Column names 

---

<a href="../pylite/lite_table.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_foreign_key_references`

```python
get_foreign_key_references() → dict
```

Returns dictionary of foreign keys associated with table. 



**Returns:**
 
 - <b>`dict`</b>:  { 
 - <b>`table_name`</b>:  [  [local_key, foreign key] ] } 

---

<a href="../pylite/lite_table.py#L204"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_table_names`

```python
get_table_names(lite_connection: LiteConnection = None) → list
```

Returns a list of all tables in database. 



**Returns:**
 
 - <b>`list`</b>:  [table_name,..] 

---

<a href="../pylite/lite_table.py#L238"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert`

```python
insert(columns, or_ignore=False)
```

Inserts row into database table. 



**Args:**
 
 - <b>`columns`</b> (dict):  { 
 - <b>`column_name`</b>:  row_value } 
 - <b>`or_ignore`</b> (bool, optional):  Ignore if row already exists. Defaults to False. 

---

<a href="../pylite/lite_table.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_pivot_table`

```python
is_pivot_table(table_name: str, lite_connection: LiteConnection = None) → bool
```

Checks if table is pivot table by counting table columns and checking foreign key references. 



**Args:**
 
 - <b>`table_name`</b> (str):  Table name 



**Returns:**
 bool 

---

<a href="../pylite/lite_table.py#L294"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `select`

```python
select(where_columns: list, result_columns: list = None) → list
```

Executes a select statement on database table. 



**Args:**
 
 - <b>`where_columns`</b> (list):  [  [column_name, ('=','<','>','LIKE'), column_value] ] 
 - <b>`result_columns`</b> (list, optional):  List of columns to include in results. Defaults to all. 



**Returns:**
 
 - <b>`list`</b>:  Query results 

---

<a href="../pylite/lite_table.py#L261"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update`

```python
update(update_columns: dict, where_columns: list, or_ignore: bool = False)
```

Updates a row in database table. 



**Args:**
 
 - <b>`update_columns`</b> (dict):  { 
 - <b>`column_name`</b>:  updated_row_value } 
 - <b>`where_columns`</b> (list):  [  [column_name, ('=','<','>','LIKE'), column_value] ] 
 - <b>`or_ignore`</b> (bool, optional):  Ignore if row already exists. Defaults to False. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
