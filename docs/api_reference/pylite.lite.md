<!-- markdownlint-disable -->

<a href="../pylite/lite.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite`
Contains the Lite class 



---

<a href="../pylite/lite.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Lite`
Helper functions for other Lite classes. 



**Raises:**
 
 - <b>`EnvFileNotFound`</b>:  Environment ('.env') file not found in script directory 
 - <b>`DatabaseNotFoundError`</b>:  Database not specified by environment file or variables. 




---

<a href="../pylite/lite.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `connect`

```python
connect(lite_connection: LiteConnection)
```

Connects to a database. 

---

<a href="../pylite/lite.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_database`

```python
create_database(database_path: str)
```

Creates an empty SQLite database. 



**Args:**
 
 - <b>`database_path`</b> (str):  Desired database location 



**Raises:**
 
 - <b>`DatabaseAlreadyExists`</b>:  Database already exists at given filepath. 

---

<a href="../pylite/lite.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `declare_connection`

```python
declare_connection(label: str, lite_connection: LiteConnection)
```

Declares a connection to a database. 

---

<a href="../pylite/lite.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `disconnect`

```python
disconnect()
```

Disconnects from the default connection. 

---

<a href="../pylite/lite.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_database_path`

```python
get_database_path() → str
```

Returns sqlite database filepath. 



**Raises:**
 
 - <b>`DatabaseNotFoundError`</b>:  Database not specified by environment file or variables. 



**Returns:**
 
 - <b>`str`</b>:  Database filepath 

---

<a href="../pylite/lite.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_env`

```python
get_env() → dict
```

Returns dict of values from .env file. 



**Raises:**
 
 - <b>`EnvFileNotFound`</b>:  Environment ('.env') file not found in script directory 



**Returns:**
 
 - <b>`dict`</b>:  Dictionary containing the key-value pairings from the .env file. 

---

<a href="../pylite/lite.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_debug_mode`

```python
set_debug_mode(debug_mode: bool = True)
```

Sets debug mode. If True, Lite will print debug messages. 



**Args:**
 
 - <b>`debug_mode`</b> (bool, optional):  Defaults to True. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
