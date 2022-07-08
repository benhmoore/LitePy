from lite.litemodel import LiteModel
from lite.litetable import LiteTable
import os

os.environ['DB_DATABASE'] = 'scratch.db'

try: os.remove('scratch.db')
except: pass

if not os.path.exists('scratch.db'):
    try: os.remove('scratch.db')
    except: pass

    LiteTable.create_database('scratch.db')

    LiteTable.create_table('users', {
        'name': 'TEXT',
        'acc_id': 'TEXT'
    },"id",{
        'acc_id':['accounts','id'],
    })

    LiteTable.create_table('accounts', {
        'username': 'TEXT',
        'password': 'TEXT',
    })

    LiteTable.create_table('pets', {
        'name': 'TEXT',
        'type': 'TEXT',
        'owner_id': 'INTEGER'
    },"id",{
        'owner_id': ['users','id']
    })

# - - - Create Models - - -

class Account(LiteModel):
    
    def user(self):
        return self.hasOne(User)

class User(LiteModel):
    
    def account(self):
        return self.belongsTo(Account)

    def pets(self):
        return self.hasMany(Pet)

class Pet(LiteModel):

    def owner(self):
        return self.belongsTo(User)
        
# - - - Generate Test Data - - -
if len(User.all()) == 0:
    user_1, user_2, user_3 = User.createMany([
        {'name': 'Ben', 'acc_id': 1},
        {'name': 'Dene', 'acc_id': 2},
        {'name': 'Rayner', 'acc_id': 3},
    ])
else:
    user_1, user_2, user_3 = User.all()

if len(Account.all()) == 0:
    acc_1, acc_2, acc_3 = Account.createMany([
        {
            'username': 'bhm128',
            'password': '123',
        },
        {
            'username': 'denemoore656',
            'password': '123',
        },
        {
            'username': 'oscarmoore',
            'password': 'iris12',
        }
    ])
else:
    acc_1, acc_2, acc_3 = Account.all()

if len(Pet.all()) == 0:
    pet_1, pet_2, pet_3 = Pet.createMany([
        {
            'name': 'Bouncer',
            'type': 'Dog',
        },
        {
            'name': 'Oreo',
            'type': 'Cat'
        },
        {
            'name': 'Iris',
            'type': 'Dog',
        },
    ])
else:
    pet_1, pet_2, pet_3 = Pet.all()



user_2.attachMany([pet_1])
user_3.attachMany([pet_2,pet_3])

print(user_2.name, user_2.account().username, [pet.name for pet in user_2.pets()])
print(user_3.name, user_3.account().username, [pet.name for pet in user_3.pets()])

print(pet_3.owner().name)
# print(user_2.name, user_2.account().username)

# acc_1.attach(user_1)
# print(user_1.account().username)
# acc_1.detach(user_1)

# user_1.attach(acc_1)
# print("Indirectly accessed name: ", user_1.account().user().name)
# print("Indirectly accessed username: ", user_1.account().user().account().username)
# user_1.detach(acc_1)

# print(user_1.account().username)

# user_1.attach(acc_1)
# pg_home.detach(pg_about)