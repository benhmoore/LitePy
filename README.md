# LitePy

**An object relational mapper (ORM) project inspired by Laravel's Eloquent, built for Python.**

## Tests: [![Coverage Status](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/benhmoore/LitePy)

This is an ongoing project to develop a better, pythonic, model-based system for database manipulation, _heavily_ inspired by Laravel's ORM, Eloquent.

The goal is to abstract away the necessity of writing SQL queries and maintaining complex relationships between tables. You can instead define readable model classes that represent tables, declare relationships between these models, and manipulate data in way that complements Python syntax.

### Database Support

LitePy currently supports SQLite (hence the name).

## Why use LitePy? A quick example.

Consider a rudimentary system that maintains a database of authors and books for a library. An author may have written one book, multiple books, or none at all. We would like to be able to relate each book with an author. That way, we can ask the system for all books written by an author or for the author of a given book. Nice and simple, right?

The database for this system consists of the following two tables:

```
authors
   - id
   - name

books
   - id
   - name
   - author_id
```

Python offers excellent support of SQLite out of the box, but you'll still need to get your hands dirty with some SQL queries.

LitePy abstracts all that away.

First, we'll define two models to represent the two tables above. These classes inherit from `LiteModel`, which will later be explored in detail. They each represent a single object, or row, in their respective tables:

```python

class Author(LiteModel):

    def books(self) -> LiteCollection:
        return this.has_many(Book)

class Book(LiteModel):

    def author(self) -> LiteModel:
        return this.belongs_to(Author)

```

...And that's it. Literally.

Now, we can operate on our data in a beautifully abstract way:

```python

# Create a new author in the database
jane = Author.create({
    'name': 'Jane Doe'
})

# Create a new book in the database
moneyBook = Book.create({
    'name': 'Make Money Fast!'
})

# "Attach" this book to the author
jane.attach(moneyBook)

moneyBook.author() # Returns the author!
jane.books() # Returns a list of her books!
```

There are a host of methods provided by LitePy for manipulating the models we've created. Methods for updating, creating, deleting, relating, and even path finding!

Of course, most use cases are orders of magnitude more complex than this example. LitePy supports all common database relationship types (has_one, has_many, belongs_to, belongs_to_many), relationships that span multiple databases, nonstandard table names, and more.

If this example piqued your interest, continue on for all the gritty details.

## Installation

To build from source, clone this repository and install a live, development version with pip:

`pip3 install -e [litepy_repo_directory]`

### Run Tests

`coverage run --omit="*/tests/*" -m pytest tests`

`coverage report --show-missing`

## Documentation

Documentation is hosted on GitHub, right over here.
