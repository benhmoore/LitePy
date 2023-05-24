<!-- markdownlint-disable -->

<a href="../pylite/lite_exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pylite.lite_exceptions`
Contains Exceptions specific for Lite  



---

<a href="../pylite/lite_exceptions.py#L4"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `EnvFileNotFound`
Raised when the environment ('.env') file is not found within the working directory. 

<a href="../pylite/lite_exceptions.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```









---

<a href="../pylite/lite_exceptions.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DatabaseNotFoundError`
Raised when a database doesn't exist at the specified filepath. 

<a href="../pylite/lite_exceptions.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(database_path)
```









---

<a href="../pylite/lite_exceptions.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DatabaseAlreadyExists`
Raised when a database already exists at the specified filepath. 

<a href="../pylite/lite_exceptions.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(database_path)
```









---

<a href="../pylite/lite_exceptions.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TableNotFoundError`
Raised when a table doesn't exist in database. 

<a href="../pylite/lite_exceptions.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(table_name)
```









---

<a href="../pylite/lite_exceptions.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ModelInstanceNotFoundError`
Raised when a model doesn't exist in the table. 

<a href="../pylite/lite_exceptions.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(model_id)
```









---

<a href="../pylite/lite_exceptions.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RelationshipError`
Raised when an error occurs during attachment or detachment between models. 

<a href="../pylite/lite_exceptions.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message)
```









---

<a href="../pylite/lite_exceptions.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DuplicateModelInstance`
Raised when more than one of the same model instance is added to a collection. 

<a href="../pylite/lite_exceptions.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
