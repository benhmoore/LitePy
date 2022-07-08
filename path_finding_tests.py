import typing
from xmlrpc.client import Boolean

class Book:
    def star(self) -> Boolean:
        return True

    def remove(self):
        return typing.get_type_hints(self.star)


a = Book()
print(a.remove())