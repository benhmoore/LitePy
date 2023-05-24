# Getting Started

PyLite is a lightweight ORM for SQLite3. It aims to provide a simple and intuitive interface for interacting with SQLite3 databases from Python.

## Concepts Background

To dive into the concepts behind PyLite, check out the [Introduction](introduction.md), which provides an overview of models and relationships.

## Installation

### Environment Requirements

| Python Version | Supported          |
| -------------- | ------------------ |
| <3.9           | :x:                |
| >=3.9          | :white_check_mark: |

PyLite is available on PyPI. The latest stable version can be installed using pip:

```bash
pip install pylite
```

## Importing PyLite
The `pylite` package provides access to the following Classes:

```python
from pylite import Lite, LiteConnection, LiteTable, LiteModel, LiteCollection, LiteQuery
```

You will probably end up using each of these classes at some point in your projects, so it would be profitable for us to take a look at them.

### `Lite`
## Creating a Database
This class provides methods for creating databases and managing connections to them. As a consequence, it is the first class you will encounter.

To create a database, you can use the `create_database` method:

```python
Lite.create_database("my_database.db")
```

This method will raise a `DatabaseAlreadyExists` exception if the database already exists.

## Connecting to a Database
To connect to a database, you can use the `connect` method:

```python
connection = LiteConnection(database_path="my_database.db")
Lite.connect(connection)
```

Here, we create a new LiteConnection instance containing a pointer to the database we want to connect to. We pass this connection to the `connect` method, establishing a default connection that can be used by other classes.

The `Lite` class has a few other methods, but these two are the most important for getting started, so for now, we will move on to `LiteConnection`.

### `LiteConnection`
## Configuring a Connection
The `LiteConnection` class is used to construct connections that are passed to  the `Lite.connect` method. For general use, you shouldn't need to interact with this class much, but it is useful to configure SQLite connection parameters, such as isolation level and journal mode.

By default, isolation is disabled and journal mode is set to `WAL`. To change these settings, you can pass the `isolation` and `journal_mode` parameters to the constructor:

```python
connection = LiteConnection(database_path="my_database.db", isolation=False, wal=True)
```

Let's continue onwards to `LiteTable`.

### `LiteTable`
## Creating a Table
The `LiteTable` class is primarily used for creating and deleting tables. After you've created and connected to a database, you can create a table using the `create_table` method:

```python
LiteTable.create_table("users", columns={
    "name": "TEXT",
    "email": "TEXT"
})
```

In this case, we're creating a `users` table with two columns: `name` and `email`. The keys in the `columns` dictionary represent the table's fields, and the values are their respective types. The data types are the same as those used by SQLite3.

## Checking if a Table Exists

You can check if a table exists using the `exists` method:

```python
LiteTable.exists("users")
```

This method returns either `True` or `False`.

## Deleting a Table

To delete a table, you can use the `delete_table` method:

```python
LiteTable.delete_table("table_name")
```

Once you've created a table, you can use `LiteModel` to interact with it.

### `LiteModel`
## Declaring a Model
Unlike the other classes we've looked at, `LiteModel` is a base class that you will inherit from to create your own models. For example, assuming we have a table called `users`, we can create a model for it like so:

```python
class User(LiteModel):
    pass
```
This is the simplest form of a model declaration. By default, the model will use the table name `users`. If your database follows a different naming scheme, you can specify it:

```python
class User(LiteModel):
    table_name = "some_other_table_name"
```

We can now use this model to interact with the `users` table.

## Creating Records with a Model
To create a new row in the `users` table, we can use the `create` method:

```python
john = User.create({
    "name": "John Doe",
    "email": "j_d@email.com"
})
```

This method returns a new instance of the model, which we can use to access the corresponding record's fields.

## Accessing a Record's Fields
We can access a record's fields directly as attributes of the model instance:

```python
print(john.name)  # John Doe
print(john.email)  # j_d@gmail
``` 

## Modifying a Record's Fields
We can modify a record's fields by assigning new values to them and then calling the `save` method:

```python
john.email = "jd@email.com"
john.save()
```

## Deleting a Record
To delete a record, we can use the `delete` method:

```python
john.delete()
```

## Finding a Record
