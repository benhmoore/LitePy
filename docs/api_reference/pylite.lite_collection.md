<!-- markdownlint-disable -->

<a href="../pylite/lite_collection.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_collection`
Contains the LiteCollection class 



---

<a href="../pylite/lite_collection.py#L5"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LiteCollection`
A collection of LiteModel instances 

<a href="../pylite/lite_collection.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(model_instances=None)
```








---

<a href="../pylite/lite_collection.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add`

```python
add(model_instance)
```

Adds a LiteModel instance to the collection. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  LiteModel instance 



**Raises:**
 
 - <b>`DuplicateModelInstance`</b>:  Model instance already exists in LiteCollection 
 - <b>`WrongModelType`</b>:  Model instance has a different table name than the existing models 

---

<a href="../pylite/lite_collection.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `attach_many_to_all`

```python
attach_many_to_all(model_instances)
```

Attaches a list of model instances to the all model instances in the collection. 



**Args:**
 
 - <b>`model_instances`</b> (list):  List of LiteModel instances 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship already exists. 

---

<a href="../pylite/lite_collection.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `attach_to_all`

```python
attach_to_all(model_instance, self_fkey: str = None, model_fkey: str = None)
```

Attaches a model instance to the all model instances in the collection. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  LiteModel instance 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship already exists. 

---

<a href="../pylite/lite_collection.py#L192"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_all`

```python
delete_all()
```

Deletes all model instances in the collection from the database. 

---

<a href="../pylite/lite_collection.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `detach_from_all`

```python
detach_from_all(model_instance)
```

Detaches a given model instance from all the model instances in the collection. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  The model instance to detach from all the model instances. 
 - <b>`self_fkey`</b> (str):  The foreign key in this model instance  that points to the other model instance (default is None). 
 - <b>`model_fkey`</b> (str):  The foreign key in the other model instance  that points to this model instance (default is None). 

---

<a href="../pylite/lite_collection.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `detach_many_from_all`

```python
detach_many_from_all(model_instances)
```

Detaches a list of model instances from all the model instances in the collection. 



**Args:**
 
 - <b>`model_instances`</b> (list):  List of LiteModel instances. 
 - <b>`self_fkey`</b> (str, optional):  Foreign key to use for the self-model. Defaults to None. model_fkey (str, optional):  Foreign key to use for the model being detached. Defaults to None. 



**Raises:**
 
 - <b>`RelationshipError`</b>:  Relationship does not exist. 

---

<a href="../pylite/lite_collection.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `difference`

```python
difference(lite_collection)
```

Returns all models not in the passed collection. 



**Args:**
 
 - <b>`lite_collection`</b> (LiteCollection):  LiteCollection instance 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Collection of LiteModel instances forming intersection 

---

<a href="../pylite/lite_collection.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `first`

```python
first()
```

Returns the first model instance in the collection. 

---

<a href="../pylite/lite_collection.py#L186"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `fresh`

```python
fresh()
```

Retrieves a fresh copy of each model instance in the collection from the database. 

---

<a href="../pylite/lite_collection.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `intersection`

```python
intersection(lite_collection)
```

Returns the intersection of two collections. 



**Args:**
 
 - <b>`lite_collection`</b> (LiteCollection):  LiteCollection instance 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Collection of LiteModel instances forming intersection 

---

<a href="../pylite/lite_collection.py#L203"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `join`

```python
join(lite_collection)
```

Merges two LiteCollection instances. 



**Args:**
 
 - <b>`lite_collection`</b> (LiteCollection):  LiteCollection instance 

---

<a href="../pylite/lite_collection.py#L170"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `last`

```python
last()
```

Returns the last model instance in the collection. 

---

<a href="../pylite/lite_collection.py#L198"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `model_keys`

```python
model_keys() → list
```

Returns a list of primary keys for models in the collection. 

---

<a href="../pylite/lite_collection.py#L248"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove`

```python
remove(model_instance)
```

Removes a LiteModel instance from this collection. 



**Args:**
 
 - <b>`model_instance`</b> (LiteModel):  LiteModel instance to remove 



**Raises:**
 
 - <b>`ModelInstanceNotFoundError`</b>:  LiteModel instance does not exist in this collection. 

---

<a href="../pylite/lite_collection.py#L175"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `sort`

```python
sort(field: str = 'id', reverse: bool = False)
```

Sorts the collection by the given field. Defaults to model's id. 



**Args:**
 
 - <b>`field`</b> (str):  Field to order by 
 - <b>`reverse`</b> (bool, optional):  Whether to reverse the order. Defaults to False. 

---

<a href="../pylite/lite_collection.py#L263"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `where`

```python
where(column_name)
```

Simulates a select query on this collection. 



**Args:**
 
 - <b>`where_columns`</b> (list):  [  [column_name, ('=','<','>','LIKE'), column_value] ] 



**Returns:**
 
 - <b>`LiteCollection`</b>:  Matching LiteModel instances 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
