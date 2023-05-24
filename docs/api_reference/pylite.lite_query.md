<!-- markdownlint-disable -->

<a href="../pylite/lite_query.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_query`
Contains the LiteQuery class  



---

<a href="../pylite/lite_query.py#L5"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LiteQuery`
This class is used to create and execute queries on a LiteModel. 

<a href="../pylite/lite_query.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(lite_model, column_name: str)
```

Initializes a new LiteQuery. 



**Args:**
 
 - <b>`lite_model`</b> (LiteModel):  The LiteModel to query. 
 - <b>`column_name`</b> (str):  The column within the LiteModel to query. 




---

<a href="../pylite/lite_query.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `all`

```python
all()
```

Executes the query and returns a LiteCollection 

---

<a href="../pylite/lite_query.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `and_where`

```python
and_where(column_name)
```

Adds an AND clause to the query 

---

<a href="../pylite/lite_query.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `contains`

```python
contains(value)
```

Checks if the column contains the value 

---

<a href="../pylite/lite_query.py#L126"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `does_not_contain`

```python
does_not_contain(value)
```

Checks if the column does not contain the value 

---

<a href="../pylite/lite_query.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ends_with`

```python
ends_with(value)
```

Checks if the column ends with the value 

---

<a href="../pylite/lite_query.py#L156"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `first`

```python
first()
```

Executes the query and returns the first result 

---

<a href="../pylite/lite_query.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_equal_to`

```python
is_equal_to(value)
```

Checks if the column is equal to the value 

---

<a href="../pylite/lite_query.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_greater_than`

```python
is_greater_than(value)
```

Checks if the column is greater than the value 

---

<a href="../pylite/lite_query.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_greater_than_or_equal_to`

```python
is_greater_than_or_equal_to(value)
```

Checks if the column is greater than or equal to the value 

---

<a href="../pylite/lite_query.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_in`

```python
is_in(values)
```

Checks if the column is in the given values list 

---

<a href="../pylite/lite_query.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_less_than`

```python
is_less_than(value)
```

Checks if the column is less than the value 

---

<a href="../pylite/lite_query.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_less_than_or_equal_to`

```python
is_less_than_or_equal_to(value)
```

Checks if the column is less than or equal to the value 

---

<a href="../pylite/lite_query.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_like`

```python
is_like(value)
```

Checks if the column is like the value 

---

<a href="../pylite/lite_query.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_not_equal_to`

```python
is_not_equal_to(value)
```

Checks if the column is not equal to the value 

---

<a href="../pylite/lite_query.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_not_like`

```python
is_not_like(value)
```

Checks if the column is not like the value 

---

<a href="../pylite/lite_query.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `last`

```python
last()
```

Executes the query and returns the last result 

---

<a href="../pylite/lite_query.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `or_where`

```python
or_where(column_name)
```

Adds an OR clause to the query 

---

<a href="../pylite/lite_query.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `starts_with`

```python
starts_with(value)
```

Checks if the column starts with the value 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
