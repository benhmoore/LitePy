# from multiprocessing.sharedctypes import Value
import pytest, sqlite3, os
from lite import *

os.environ['DB_DATABASE'] = 'pytest.sqlite'

# Create models for tests
class User(LiteModel):
    
    def parent(self):
        return self.belongsTo(User,'user_id')

    def child(self):
        return self.hasOne(User)

    def cars(self):
        return self.belongsToMany(Car)

    def bank_account(self):
        return self.hasOne(Bank_Account)

    def products(self):
        return self.hasMany(Product)


def test_get_length():
    """Tests to see if length of collection can be accurately attained."""

    collection = LiteCollection()
    assert len(collection) == 0

    del collection

def test_add():
    """Tests adding to LiteCollection instance."""

    collection = LiteCollection()

    user_1 = User.create({"username":'ben',"password":'123'})
    user_2 = User.create({"username":'toby',"password":'123'})
    user_3 = User.create({"username":'ike',"password":'123'})

    collection.add(user_1)
    collection.add(user_2)
    collection.add(user_3)
    
    assert collection == LiteCollection([user_1, user_2, user_3])

    del collection

def test_add_duplicate():
    """Tests adding to LiteCollection instance."""

    collection = LiteCollection()

    user_1 = User.create({"username":'ben',"password":'123'})

    collection.add(user_1)
    
    with pytest.raises(DuplicateModelInstance):
        collection.add(user_1)

    del collection

def test_remove():
    """Tests removing from LiteCollection instance."""

    collection = LiteCollection()

    user_1, user_2, user_3 = User.all()[:3]

    collection.add(user_1)
    collection.add(user_2)
    collection.add(user_3)

    collection.remove(user_1)
    collection.remove(user_3)
    
    assert collection == LiteCollection([user_2])

def test_equality():
    """Tests comparisons of LiteCollection instances."""

    c_1 = LiteCollection()

    user_1, user_2, user_3 = User.all()[:3]

    c_1.add(user_1)
    c_1.add(user_2)
    c_1.add(user_3)

    c_2 = LiteCollection()
    c_2.add(user_1)
    c_2.add(user_2)
    c_2.add(user_3)

    assert c_1 == c_2
    
def test_contains():
    """Tests the 'in' operator of LiteCollection instances."""

    user_1, user_2, user_3 = User.all()[:3]

    c_1 = LiteCollection([user_1, user_3])

    c_1.remove(user_1)

    assert user_1 not in c_1
    assert user_2 not in c_1
    assert user_3 in c_1

