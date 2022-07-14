import pytest, sqlite3, os
from lite.litemodel import LiteModel, LiteCollection
from lite.litetable import LiteTable
from lite.liteexceptions import *

os.environ['DB_DATABASE'] = 'pytest.db'

# Setup database
test_db = 'pytest.db'
try: os.remove('pytest.db')
except Exception: pass

LiteTable.create_database(test_db)

# Create models for tests
class User(LiteModel):
    
    def parent(self) -> LiteModel:
        return self.belongsTo(User,'user_id')

    def child(self) -> LiteModel:
        return self.hasOne(User)

    def cars(self) -> LiteCollection:
        return self.belongsToMany(Car)

    def bank_account(self) -> LiteModel:
        return self.hasOne(Bank_Account)

    def products(self) -> LiteCollection:
        return self.hasMany(Product)

class Car(LiteModel):
    
    def owners(self) -> LiteCollection:
        return self.belongsToMany(User)

class Bank_Account(LiteModel):
    
    def holder(self) -> LiteModel:
        return self.belongsTo(User)

class Product(LiteModel):
    
    def owner(self) -> LiteModel:
        return self.belongsTo(User)


# Create tables for tests - - - - -

# Users table
LiteTable.create_table('users', {
    'username': 'TEXT',
    'password': 'TEXT',
    'user_id': 'INTEGER'   
},{
    'user_id':['users','id']
})

# Cars table
# A car can belong to  one or more people, and one person may own multiple cars
LiteTable.create_table('cars', {
    'make': 'TEXT',
    'model': 'TEXT',
})

# Pivot table
LiteTable.create_table('car_user', {
    'cid': 'INTEGER',
    'uid': 'INTEGER',
},{
    "cid":['cars','id'],
    "uid":['users','id']
})

# Bank Account table
LiteTable.create_table('bank_accounts',{
    'account_number': 'INTEGER',
    'routing_number': 'INTEGER',
    'user_id': 'INTEGER',
},{
    "user_id":['user','id']
})

# Products table
LiteTable.create_table('products',{
    'manufacturer': 'TEXT',
    'user_id': 'INTEGER'
},{
    "user_id":['user','id']
})

# Test .create()
@pytest.mark.parametrize("columns, expected", [
    ({
        'username':'john',
        'password':'123'
    }, 1),
    ({
        'username':'jane',
        'password':'123'
    }, 2),
])
def test_create_users(columns, expected):
    user = User.create(columns)
    assert len(user.table.select([])) == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'make':'VW',
        'model':'Jetta'
    }, 1),
    ({
        'make':'Toyota',
        'model':'Sequoia'
    }, 2),
])
def test_create_cars(columns, expected):
    car = Car.create(columns)
    assert len(Car.all()) == expected
    assert car.id == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'account_number':124123,
        'routing_number':124123
    }, 1),
    ({
        'account_number':999999,
        'routing_number':999999
    }, 2),
])
def test_create_bank_accounts(columns, expected):
    bankAccount = Bank_Account.create(columns)
    assert len(Bank_Account.all()) == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'manufacturer':'Apple, Inc.',
    }, 1),
    ({
        'manufacturer':'Dell, Inc.',
    }, 2),
])

def test_create_products(columns, expected):
    product = Product.create(columns)
    print(product.id)
    assert len(Product.all()) == expected

# Test .attach() and all relationships
def test_attach():
    user_a = User.findOrFail(1)
    user_b = User.findOrFail(2)

    car_1 = Car.where([['make','=','VW']])[0]
    bank_acc = Bank_Account.all().where([['account_number','>',125000]])[0]

    product_a = Product.findOrFail(1)
    product_b = Product.findOrFail(2)

    user_b.attach(user_a)
    user_b.attach(car_1)
    
    user_a.attach(bank_acc)

    user_b.attach(product_a)
    user_b.attach(product_b)

    assert user_a.child().username == "jane"
    assert user_a.child().username == "jane"

    # Test Many-To-Many relationships using Pivot Table
    assert user_b.cars()[0].make == "VW"
    assert car_1.owners()[0].username == "jane"

    assert bank_acc.holder().username == "john"
    assert user_b.parent().username == "john"
    assert len(user_b.products()) == 2
    assert product_a.owner().username == "jane"

# Test .detach()
def test_detach():
    user_a = User.findOrFail(1)
    bank_acc = Bank_Account.findOrFail(2)
    user_a.detach(bank_acc)

    assert user_a.bank_account() == None

def test_detach_pivot():
    user_b = User.findOrFail(2)
    car = Car.findOrFail(1)

    assert len(user_b.cars()) == 1
    
    user_b.detach(car)
    assert len(user_b.cars()) == 0

# Test .save()
def test_save():
    user_a = User.findOrFail(1)
    user_a.password = 'xyz'
    user_a.save()

    user_temp = User.findOrFail(1)

    assert user_temp.password == 'xyz'

# Test .delete()
def test_delete():

    # Make sure model instance exists
    user_a = User.findOrFail(1)
    assert user_a.username == 'john'

    user_a.delete()

    # Trying to delete a model instance twice should raise an exception
    with pytest.raises(ModelInstanceNotFoundError):
        user_a.delete()

    # The model shouldn't be found, since it should have been deleted.
    with pytest.raises(ModelInstanceNotFoundError):
        temp_user = User.findOrFail(1)

    # the python object should be cleared of the deleted model instance's data
    assert user_a.username == None

def test_comparisons():
    user_a, user_b, user_c = User.createMany([
        {
            'username': 'a',
            'password': 'p'
        },
        {
            'username': 'b',
            'password': 'p'
        },
        {
            'username': 'c',
            'password': 'p'
        }
    ])

    collection = sorted(LiteCollection([user_a,user_b,user_c]))


# Path finding tests
def test_find_path():

    user_a, user_b, user_c = User.createMany([
        {
            'username': 'a',
            'password': 'p'
        },
        {
            'username': 'b',
            'password': 'p'
        },
        {
            'username': 'c',
            'password': 'p'
        }
    ])


    car_1, car_2 = Car.all()

    user_a.attach(car_2)
    car_2.attach(user_b)

    user_b.attach(car_1)
    car_1.attach(user_c)

    acc_1 = Bank_Account.create({
        'account_number':'6969'
    })


    user_c.attach(acc_1)

    assert user_a.findPath(car_1) != False
    assert car_2.findPath(user_a) != False
    assert user_a.findPath(user_b) != False
    assert len(user_a.findPath(acc_1)) == 6
    assert len(user_a.findPath(acc_1)) == 6
    

    # assert False == True