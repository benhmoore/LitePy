<!-- markdownlint-disable -->

<a href="../pylite/lite_model.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_model`
Contains the LiteModel class definition 



---

<a href="../pylite/lite_model.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LiteModel`
Describes a distinct model for database storage and methods for operating upon it. 



**Raises:**
 
 - <b>`TypeError`</b>:  Comparison between incompatible types. 
 - <b>`ModelInstanceNotFoundError`</b>:  Model does not exist in database. 
 - <b>`RelationshipError`</b>:  Relationship does not match required status. 

<a href="../pylite/lite_model.py#L224"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    _id: int = None,
    _table: LiteTable = None,
    _values: list = None,
    _lite_conn: LiteConnection = None
)
```

LiteModel initializer. Parameters are used by internal methods and should not be provided. 




---

<a href="../pylite/lite_model.py#L450"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `accessed_through`

```python
accessed_through(lite_connection: LiteConnection)
```

Declares the connection Lite should use for this model. 



**Args:**
  lite_connection (LiteConnection):  Connection pointed to the database in which this model is stored 

---

<a href="../pylite/lite_model.py#L342"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `all`

```python
all() → LiteCollection
```

Returns a LiteCollection containing all instances of this model. 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Collection of all model instances 

---

<a href="../pylite/lite_model.py#L484"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `attach`

```python
attach(model_instance, self_fkey: str = None, model_fkey: str = None)
```

Defines a relationship between two model instances. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  Model instance to attach to self. 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship already exists. 

---

<a href="../pylite/lite_model.py#L567"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `attach_many`

```python
attach_many(model_instances)
```

Defines relationships between the current model instance and many model instances. 



**Args:**
 
 - <b>`model_instances`</b> (list, LiteCollection):  Model instances to attach to self. 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship already exists. 

---

<a href="../pylite/lite_model.py#L718"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `belongs_to`

```python
belongs_to(model, foreign_key: str = None)
```

Defines the current model instance as a child of the passed model class. 



**Args:**
 
 - <b>`model`</b> (LiteModel):  Parent model class 
 - <b>`foreign_key`</b> (str, optional):  Custom foreign key name.  Defaults to standard naming convention, 'model_id'. 



**Returns:**
 
 - <b>`LiteModel`</b>:  Parent model instance 

---

<a href="../pylite/lite_model.py#L794"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `belongs_to_many`

```python
belongs_to_many(model) → LiteCollection
```

Defines a many-to-many relationship between the current model instance and a model class. 



**Args:**
 
 - <b>`model`</b> (LiteModel):  Sibling model class 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Sibling model instances 

---

<a href="../pylite/lite_model.py#L377"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `create`

```python
create(column_values: dict)
```

Creates a new instance of a LiteModel and returns it. 



**Args:**
 
 - <b>`column_values`</b> (dict):  The initial values to be stored for this model instance. 



**Returns:**
 
 - <b>`LiteModel`</b>:  Created model instance. 

---

<a href="../pylite/lite_model.py#L414"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `create_many`

```python
create_many(column_list: list) → LiteCollection
```

Creates many new instances of a LiteModel and returns them within a LiteCollection. 



**Args:**
 
 - <b>`column_values`</b> (dict):  The initial values to be stored for this model instance. 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Created model instances. 

---

<a href="../pylite/lite_model.py#L672"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete`

```python
delete()
```

Deletes the current model instance. 



**Raises:**
 
 - <b>`ModelInstanceNotFoundError`</b>:  Model does not exist in database. 

---

<a href="../pylite/lite_model.py#L580"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `detach`

```python
detach(model_instance)
```

Removes a relationship between two model instances. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  Model instance to detach from self. 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship does not exist. 

---

<a href="../pylite/lite_model.py#L659"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `detach_many`

```python
detach_many(model_instances)
```

Removes relationships between the current model instance and many model instances. 



**Args:**
 
 - <b>`model_instances`</b> (list, LiteCollection):  Model instances to detach from self. 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship does not exist. 

---

<a href="../pylite/lite_model.py#L324"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `find`

```python
find(_id: int)
```

Returns a LiteModel instance with id matching the passed value or None. 



**Args:**
 
 - <b>`id`</b> (int):  Id of model instance within database table 



**Returns:**
 
 - <b>`LiteModel`</b>:  LiteModel with matching id or None 

---

<a href="../pylite/lite_model.py#L293"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `find_or_fail`

```python
find_or_fail(_id: int)
```

Returns a LiteModel instance with id matching the passed value. Throws an exception if an instance isn't found. 



**Args:**
 
 - <b>`id`</b> (int):  Id of model instance within database table 



**Raises:**
 
 - <b>`ModelInstanceNotFoundError`</b>:  Model does not exist in database. 



**Returns:**
 
 - <b>`LiteModel`</b>:  LiteModel with matching id 

---

<a href="../pylite/lite_model.py#L873"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_path`

```python
find_path(to_model_instance, max_depth: int = 100)
```

Attempts to find a path from the current model instance to another using Bidirectional BFS. 



**Args:**
 
 - <b>`to_model_instance`</b> (LiteModel):  Model instance to navigate to 
 - <b>`max_depth`</b> (int, optional):  Maximum depth to traverse. Defaults to 100. 



**Returns:**
 
 - <b>`LiteCollection or bool`</b>:  Either the path or False for failure 

---

<a href="../pylite/lite_model.py#L142"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_path_iter`

```python
find_path_iter(open_n: list, closed_n: list, to_model_inst)
```

Internal method. Step function for .find_path(). 

---

<a href="../pylite/lite_model.py#L707"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `fresh`

```python
fresh()
```

Reloads the model's attributes from the database. 

---

<a href="../pylite/lite_model.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_foreign_key_column_for_model`

```python
get_foreign_key_column_for_model(model) → str
```

Derives name of foreign key within current instance that references passed-in model. 

This is used to get the `primary key` value of the parent or child to this model. For example, if a `User` belongs to an `Account`, calling this method on `User` and passing in `Account` would return the name of the foreign key column referencing the particular `Account` instance the current `User` belongs to. 


- Called by attach(), detach(), belongs_to(), has_one(), and has_many(). 



**Args:**
 
 - <b>`model`</b> (LiteModel):  LiteModel class or instance 



**Returns:**
 
 - <b>`str`</b>:  Name of foreign key column referencing `parent` model instance 

---

<a href="../pylite/lite_model.py#L752"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_foreign_key_column_names`

```python
get_foreign_key_column_names(foreign_keys, model_instance)
```

Returns the foreign keys for a given model instance. 

---

<a href="../pylite/lite_model.py#L739"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_pivot_table`

```python
get_pivot_table(model)
```

Returns the pivot table for a given sibling model. 

---

<a href="../pylite/lite_model.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_relationship_methods`

```python
get_relationship_methods() → list
```

Returns a list of method names that define model-model relationships. 

To ensure methods are correctly identified as relationship definitions, make sure to specify a return type of `LiteCollection` or `LiteModel` when defining them. 



**Returns:**
 
 - <b>`list`</b>:  List of method names as strings 

---

<a href="../pylite/lite_model.py#L772"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_relationships`

```python
get_relationships(pivot_table, self_fkey, model_fkey)
```

Returns the many-to-many relationships for a given pivot table, self foreign key, and model foreign key. 

---

<a href="../pylite/lite_model.py#L849"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `has_many`

```python
has_many(model, foreign_key: str = None) → LiteCollection
```

Defines the current model instance as a parent of many of the passed model class. 



**Args:**
 
 - <b>`model`</b> (LiteModel):  Children model class foreign_key (str, optional):  Custom foreign key name. Defaults to standard naming convention, 'model_id'. 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Children model instances 

---

<a href="../pylite/lite_model.py#L820"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `has_one`

```python
has_one(model, foreign_key: str = None)
```

Reverse of belongs_to. Defines the current model instance as a parent of the passed model class. 



**Args:**
 
 - <b>`model`</b> (LiteModel):  Child model class foreign_key (str, optional):  Custom foreign key name. Defaults to standard naming convention, 'model_id'. 



**Returns:**
 
 - <b>`LiteModel`</b>:  Child model instance 

---

<a href="../pylite/lite_model.py#L428"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `pivots_with`

```python
pivots_with(
    other_model,
    table_name: str,
    lite_connection: LiteConnection = None
)
```

Notifies Lite of a many-to-many relationship. 



**Args:**
 
 - <b>`other_model`</b> (LiteModel):  The other model forming the many-to-many relationship. 
 - <b>`table_name`</b> (str):  Name of the pivot table storing the relationships. lite_connection (LiteConnection, optional):  A connection to the database in which the pivot table is stored. If the pivot table  exists in the same database as the models, this argument can be omitted. 

---

<a href="../pylite/lite_model.py#L265"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `requires_table`

```python
requires_table(
    columns: dict[str, str],
    foreign_keys: dict[str, list[str, str]] = None,
    lite_connection: LiteConnection = None
)
```

Creates a database table for the LiteModel if it doesn't exist. 



**Args:**
 
 - <b>`table_name`</b> (str):  Table name 
 - <b>`columns`</b> (dict):  { 
 - <b>`column_name`</b>:  field_attributes } 
 - <b>`foreign_keys`</b> (dict, optional):  { 
 - <b>`column_name`</b>:  [foreign_table_name, foreign_column_name] } 

---

<a href="../pylite/lite_model.py#L690"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save()
```

Saves any changes to model instance attributes. 

---

<a href="../pylite/lite_model.py#L461"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict() → dict
```

Converts LiteModel instance into human-readable dict, truncating string values if necessary. 



**Returns:**
 
 - <b>`dict`</b>:  LiteModel attributes as dictionary 

---

<a href="../pylite/lite_model.py#L364"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `where`

```python
where(column_name: str) → LiteQuery
```

Returns a new LiteQuery instance. 



**Args:**
 
 - <b>`column_name`</b> (str):  Name of column to query 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Collection of matching model instances 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
