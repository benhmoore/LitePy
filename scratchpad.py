from lite.litemodel import LiteModel
from lite.litetable import LiteTable
import os

os.environ['DB_DATABASE'] = 'scratch.db'

if not os.path.exists('scratch.db'):
    try: os.remove('scratch.db')
    except: pass

    LiteTable.create_database('scratch.db')

    LiteTable.create_table( 'scratch.db', 'users', {
        'name': 'TEXT',
        'acc_id': 'TEXT'
    },"id",{
        'acc_id':['accounts','id'],
    })

    LiteTable.create_table( 'scratch.db', 'accounts', {
        'username': 'TEXT',
        'password': 'TEXT',
    })

class Account(LiteModel):
    
    def user(self):
        return self.hasOne(user)

class User(LiteModel):
    
    def account(self):
        return self.belongsTo(Account)

if len(User.all().where([['name','=','Ben']])) == 0:
    user_1 = User.create({
        'name': 'Ben',
    })
else:
    user_1 = User.findOrFail(1)

if len(Account.all().where([['username','=','bhm128']])) == 0:
    pg_about = Account.create({
        'username': 'bhm128',
        'password': '123',
    })
else:
    acc_1 = Account.all().where([['username','=','bhm128']])[0]


acc_1.attach(user_1)
# user_1.attach(acc_1)
# pg_home.detach(pg_about)

# print(user_1.account().username)