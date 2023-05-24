# Introduction to PyLite

PyLite offers a straight-forward Object Relational Mapper (ORM) implementation for SQLite databases. It is designed to be lightweight and easy to use – offering a decidedly more Pythonic interface than the standard sqlite3 module.

PyLite is designed to be used in a similar fashion to Laravel's Eloquent ORM. If you are familiar with Eloquent, the learning curve for PyLite should be minimal.

## Introduction to the Fundamentals

In essence, PyLite is a wrapper around the standard sqlite3 module that provides abstractions for the often-laborious task of interfacing with databases. The ultimate hope is that you won't be writing SQL queries anymore.

However, to understand how to use PyLite, we'll need to cover a handful of basic concepts that enable PyLite to work its magic: models, instances, and relationships.

### Models and Instances

A model is a class that represents a database table. For example, consider a database with a `users` table, with each row representing a user. A model provides an interface for interacting with the `users` table directly from Python.

Typically, a model's name will follow the singular form of the table name, so in the case of our `users` table, the model class would be named `User`.

```mermaid
graph LR
    T[Table] <-- Represents --- M[Model]
    M -- Creates --> MI[Model Instance]
    MI -- Queries/Modifies --> T
```

An instance of the model class represents a single row in the table -- in this example, a single user, providing an intuitive interface for querying and modifying the row.

#### What does this look like?

Consider our example of a `User` model representing a `users` table.

Let's say the `users` table looks like this:
| id | name | email |
|----|------|-------|
| 1 | Alice | a@email.com |
| 2 | Bob | b@email.com |
| 3 | Carol| c@email.com |

Let's examine the simple task of pulling the first user's name and email. Using the sqlite3 module, you might write something like this:

```python
sqlite3.execute("SELECT name, email FROM users WHERE id = 1")
result = sqlite3.fetchone()
result[0] # Alice
result[1] # a@email.com
```

Using PyLite model, you could write:

```python
alice = User.find(1)
alice.name # Alice
alice.email # a@email.com
```

Don't worry if you don't understand the syntax yet, (we'll cover it soon,) but hopefully you can see how much more readable the PyLite version is. That's the beauty of models, and as your commands become more complex, improvements to readability will become increasingly apparent.

### Relationships

In order to effectively utilize PyLite's relationship features, it's important to possess a basic understanding of database relationships. Although this is outside of the scope of this documentation, we'll cover a few basic concepts here.

Relationships are a way of linking models together. For example, consider a `posts` table, with each row representing a post. Each post belongs to a user, so the `posts` table has a `user_id` column that references the `id` column of the `users` table.

The general relationship between the `users` and `posts` tables can be visualized:

```mermaid
graph TD
    U[users] -- Has Many --> P[posts]
    P -- Belongs To --> U
```

_This common relationship is referred to as a "one-to-many" relationship. In this case, a user can have many posts, but a post can only belong to one user._

Taking a peek inside these two tables, we can see the following attributes:
| users | posts |
|-------|-------|
| id | id |
| name | user_id |
| email | title |
| | body |

The `users` table should be familiar to us, and the `posts` table is relatively uncomplicated. One notable aspect, however, is the column: `user_id`. This column references the `id` column of the `users` table, enabling the one to many relationship.

To see this in action, let's take a look at a few rows from the `posts` table:
| id | user_id | title | body |
|----|---------|-------|------|
| 1 | 1 | Post 1 | This is the first post. |
| 2 | 1 | Post 2 | This is the second post. |

This table contains two posts, both of which belong to the user with an `id` of `1`. If you reference the `users` table, you'll see that user `1` is Alice.

Defining and maintaining even a simple relationship like this can be a tedious with raw SQL. PyLite aims to make this process as simple as possible. Let's briefly compare the sqlite3 module and PyLite when dealing with relationships:

#### Standard SQL

```python
# Create a new user, Daniel
sqlite3.execute("INSERT INTO users (name, email) VALUES ('Daniel', 'd@email.com')")

# Create a new post for Daniel
sqlite3.execute("INSERT INTO posts (user_id, title, body) VALUES (4, 'Post 3', 'This is the third post.')")

# Find all posts belonging to Daniel
sqlite3.execute("SELECT * FROM posts WHERE user_id = 4")
results = sqlite3.fetchall()
print(results)
```

#### PyLite

```python
# Create a new user, Daniel
daniel = User.create({
    'name': 'Daniel',
    'email': 'd@email.com'
})

# Create a new post for Daniel
post = Post.create({
    'title': 'Post 3',
    'body': 'This is the third post.'
})

# Associate the post with Daniel
daniel.attach(post)

# Get all posts belonging to Daniel
print(daniel.posts)
```

Although the PyLite version is slightly longer, it is more readable and intuitive. Your database interactions no longer feel second-class to your Python code.
