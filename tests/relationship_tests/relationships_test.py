import pytest, sqlite3, os
from lite import *

relationship_database = 'rel.sqlite'
os.environ['DB_DATABASE'] = relationship_database

try: os.remove(relationship_database)
except: pass

LiteTable.createDatabase(relationship_database)

LiteTable.createTable('users', {
    'name': 'TEXT',
    'acc_id': 'TEXT'
},{
    'acc_id':['accounts','id'],
})

LiteTable.createTable('genders', {
    'label': 'TEXT',
})

LiteTable.createTable('gender_user', {
    'uid': 'INTEGER',
    'gid': 'INTEGER'
}, {
    'uid': ['users','id'],
    'gid': ['genders','id'],
})

LiteTable.createTable('accounts', {
    'username': 'TEXT',
    'password': 'TEXT',
})

LiteTable.createTable('pets', {
    'name': 'TEXT',
    'type': 'TEXT',
    'owner_id': 'INTEGER'
},{
    'owner_id': ['users','id']
})

# - - - Create Models - - -

class User(LiteModel):
    
    def account(self):
        return self.belongsTo(Account)

    def genders(self):
        return self.belongsToMany(Gender)

    def pets(self):
        return self.hasMany(Pet)

class Gender(LiteModel):
    
    def users(self):
        return self.belongsToMany(User)

class Account(LiteModel):
    
    def user(self):
        return self.hasOne(User)

class Pet(LiteModel):

    def owner(self):
        return self.belongsTo(User)
        
# - - - Generate Test Data - - -
user_1, user_2, user_3 = User.createMany([
    {'name': 'Ben'},
    {'name': 'Dene'},
    {'name': 'Rayner'},
])

gender_1, gender_2, gender_3 = Gender.createMany([
    {'label': 'Non-Binary'},
    {'label': 'Female'},
    {'label': 'Male'},
])

acc_1, acc_2, acc_3 = Account.createMany([
    {'username': 'bhm128', 'password': '123'},
    { 'username': 'denemoore656', 'password': '123'},
    { 'username': 'oscarmoore', 'password': 'iris12'}
])

pet_1, pet_2, pet_3 = Pet.createMany([
    {'name': 'Bouncer', 'type': 'Dog'},
    {'name': 'Oreo', 'type': 'Cat'},
    {'name': 'Iris', 'type': 'Dog'},
])

def test_hasOne_belongsTo():

    # Forwards
    user_1.attach(acc_1)
    assert user_1.account().username == acc_1.username
    assert acc_1.user().name == user_1.name
    
    user_1.detach(acc_1)
    assert user_1.account() == None
    assert acc_1.user() == None

    # Backwards
    acc_1.attach(user_1)
    assert user_1.account().username == acc_1.username
    assert acc_1.user().name == user_1.name

    acc_1.detach(user_1)
    assert user_1.account() == None
    assert acc_1.user() == None

    user_1.attach(acc_1) # re-attached for later tests

def test_hasMany():

    # Forwards
    user_1.attachMany([pet_1,pet_2])
    assert [pet.name for pet in user_1.pets()] == [pet_1.name, pet_2.name]
    assert pet_1.owner().name == user_1.name
    
    user_1.detach(pet_1)
    user_1.detach(pet_2)
    assert user_1.pets() == []
    assert pet_1.owner() == None

    # Backwards
    pet_1.attach(user_1)
    pet_2.attach(user_1)
    assert [pet.name for pet in user_1.pets()] == [pet_1.name, pet_2.name]
    assert pet_1.owner().name == user_1.name

    pet_1.detach(user_1)
    pet_2.detach(user_1)
    assert user_1.pets() == []
    assert pet_1.owner() == None


def test_belongsToMany():

    # Forwards
    user_1.attachMany([gender_1, gender_3])
    user_3.attach(gender_3)
    assert [gender.label for gender in user_1.genders()] == [gender_1.label, gender_3.label]
    assert [user.name for user in gender_3.users()] == [user_1.name, user_3.name]

    user_1.detachMany([gender_1, gender_3])
    user_3.detach(gender_3)

    assert user_1.genders() == []
    assert gender_1.users() == []
    assert gender_3.users() == []

    # Backwards
    gender_1.attach(user_1)
    gender_3.attachMany([user_1, user_3])
    assert [gender.label for gender in user_1.genders()] == [gender_1.label, gender_3.label]
    assert [user.name for user in gender_3.users()] == [user_1.name, user_3.name]

    gender_1.detach(user_1)
    gender_3.detachMany([user_1, user_3])

    assert user_1.genders() == []
    assert gender_1.users() == []
    assert gender_3.users() == []

    # Test multiple attachments
    user_1.attach(gender_1)
    user_1.attach(gender_2)
    user_1.attach(gender_3)

    assert user_1.genders() == LiteCollection([gender_1, gender_2, gender_3])

    gender_3.detach(user_1)
    gender_3.attach(user_1)

    # Test duplicate attachments
    with pytest.raises(RelationshipError):
        user_1.attach(gender_3)


def test_relationship_overrides():

    user_1.attach(pet_1)

    # You cannot detach a model that was never attached
    with pytest.raises(RelationshipError):
        user_1.detach(pet_2)

    # You cannot attach the same model twice
    with pytest.raises(RelationshipError):
        user_1.attach(pet_1)

    # You cannot attach a model if another is already attached
    with pytest.raises(RelationshipError):
        pet_1.attach(user_2)

def test_delete_relationships():
    """Tests if all relationships are removed when a model instance is deleted."""

    # Make any number of random attachments in addition to those of prior tests
    pet_2.attach(user_1)

    # First, assert that these attachments are still present
    assert user_1.genders() == LiteCollection([gender_1, gender_2, gender_3])
    assert [pet.name for pet in user_1.pets()] == [pet_1.name, pet_2.name]
    assert user_1.account() == acc_1

    # Test removal of many-to-many relationship on delete
    user_2.attachMany([gender_2,gender_3])
    assert user_2 in gender_3.users()
    user_2.delete()
    assert user_2 not in gender_3.users()

    # Test removal of hasOne relationship on delete
    assert user_1.account() == acc_1
    acc_1.delete()
    assert user_1.account() == None

    # Additional test removal of many-to-many relationship on delete
    user_1.delete()
    assert gender_1.users().where([['name','=','Ben']]) == []
    assert Pet.all().where([['owner_id','=',1]]) == []
    # assert 1 == 2



    