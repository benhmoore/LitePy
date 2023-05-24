<!-- markdownlint-disable -->

<a href="../pylite/lite_connection.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_connection`
Contains the LiteConnection class and DB Enum 



---

<a href="../pylite/lite_connection.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LiteConnection`
This class is used to create a connection to a database and execute queries. 

<a href="../pylite/lite_connection.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    database_path: str = None,
    isolation: bool = False,
    wal: bool = True
) → None
```








---

<a href="../pylite/lite_connection.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close() → None
```

Closes the connection to the database. 

---

<a href="../pylite/lite_connection.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute`

```python
execute(sql_str: str, values: tuple = ()) → ExecuteResult
```

Executes a query on the database. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
