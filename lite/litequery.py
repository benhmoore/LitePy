""" Contains the LiteQuery class """
from lite import LiteTable, LiteModel, Lite
# from lite.liteexceptions import ModelInstanceNotFoundError, RelationshipError

class LiteQuery:
    def __init__(self, lite_model: LiteModel, column_name: str):
        self.model = lite_model
        self.where_clause = f" WHERE {column_name}"

    # def where(self, column_name):
    #     self.where_clause = f" WHERE {column_name}"
    #     return self

    def isEqualTo(self, value):
        self.where_clause += f" = '{value}'"
        return self

    def isNotEqualTo(self, value):
        self.where_clause += f" != '{value}'"
        return self

    def isGreaterThan(self, value):
        self.where_clause += f" > '{value}'"
        return self

    def isGreaterThanOrEqualTo(self, value):
        self.where_clause += f" >= '{value}'"
        return self

    def isLessThan(self, value):
        self.where_clause += f" < '{value}'"
        return self

    def isLessThanOrEqualTo(self, value):
        self.where_clause += f" <= '{value}'"
        return self

    def isLike(self, value):
        self.where_clause += f" LIKE '{value}'"
        return self

    def isNotLike(self, value):
        self.where_clause += f" NOT LIKE '{value}'"
        return self

    def startsWith(self, value):
        self.where_clause += f" LIKE '{value}%'"
        return self

    def endsWith(self, value):
        self.where_clause += f" LIKE '%{value}'"
        return self

    def contains(self, value):
        self.where_clause += f" LIKE '%{value}%'"
        return self

    def orWhere(self, column_name):
        self.where_clause += f" OR {column_name}"
        return self

    def andWhere(self, column_name):
        self.where_clause += f" AND {column_name}"
        return self

    def all(self):

        print(self.model)
        table_name = self.model.pluralize(self.model, self.model.__name__.lower())

        if self.model.DEFAULT_CONNECTION is not None:
            lite_connection = self.model.DEFAULT_CONNECTION
        else:
            lite_connection = Lite.DEFAULT_CONNECTION

        if hasattr(self.model, 'table_name'):
            table_name = self.model.table_name

        table = LiteTable(table_name, lite_connection)

        query = f"SELECT * FROM {self.model.table_name}{self.where_clause}"
        
        return table.connection.execute(query, tuple()).fetchall()

    def first(self):
        return self.all()[0]
    
    def last(self):
        return self.all()[-1]

        