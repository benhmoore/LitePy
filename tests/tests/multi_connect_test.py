import pytest, sqlite3, os
from lite import *

# Setup database
try: os.remove('db_1.sqlite')
except Exception: pass

try: os.remove('db_2.sqlite')
except Exception: pass

Lite.createDatabase('db_1.sqlite')
Lite.createDatabase('db_2.sqlite')

c1 = LiteConnection(DB.SQLITE, database_path='db_1.sqlite')
c2 = LiteConnection(DB.SQLITE, database_path='db_2.sqlite')

class Attribute(LiteModel):

    def seasons(self) -> LiteCollection:
        return self.belongsToMany(Season)

class Season(LiteModel):

    def months(self) -> LiteCollection:
        return self.hasMany(Month)

    def attributes(self) -> LiteCollection:
        return self.belongsToMany(Attribute)

class Month(LiteModel):
    
    def season(self) -> LiteModel:
        return self.belongsTo(Season)

Attribute.accessedThrough(c1)
Season.accessedThrough(c2)
Month.accessedThrough(c1)

LiteTable.createTable('months', {

    'name': 'text',
    'season_id': 'integer'

}, {
    'season_id': ['seasons', 'id']
}, lite_connection=c1)

LiteTable.createTable('seasons', {
    
    'name': 'text'

}, lite_connection=c2)

LiteTable.createTable('attributes', {

    'description': 'text'

}, lite_connection=c1)

LiteTable.createTable('attribute_season', {

    'attribute_id': 'integer',
    'season_id': 'integer'
},
{
    'attribute_id': ['attributes', 'id'],
    'season_id': ['seasons', 'id'],
}, c2)

Season.pivotsWith(Attribute, 'attribute_season', c2)


spring, summer, fall, winter = Season.createMany([
    {'name': 'Spring'}, {'name': 'Summer'}, {'name': 'Fall'}, {'name': 'Winter'}
])


january, february, december = Month.createMany([
    {'name':'January'}, {'name':'February'}, {'name':'December'}
])

new_growth, freezing, hot = Attribute.createMany([
    {'description': 'New growth'}, {'description': 'Freezing temperatures'}, {'description': 'High temperatures'}
])


spring.attachMany([january, february, new_growth, freezing])

freezing.attachMany([fall, winter])

hot.attachMany([summer, fall])

print(hot.seasons())


def test_remove_databases():
    try: os.remove('db_1.sqlite')
    except Exception: pass

    try: os.remove('db_2.sqlite')
    except Exception: pass