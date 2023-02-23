from lite import *

class Pet(LiteModel):

    def owner(self) -> LiteModel:
        return self.belongsTo(Person)

class Brain(LiteModel):

    def owner(self) -> LiteModel:
        return self.belongsTo(Person)

class Membership(LiteModel):
    
    def people(self) -> LiteModel:
        return self.belongsToMany(Person)

class DollarBill(LiteModel):

    TABLE_NAME = "dollar_bills"

    def owner(self) -> LiteModel:
        return self.belongsTo(Person)

class Person(LiteModel):

    TABLE_NAME = "people"

    def pets(self) -> LiteModel:
        return self.hasMany(Pet)

    def brain(self) -> LiteModel:
        return self.hasOne(Brain)

    def memberships(self) -> LiteModel:
        return self.belongsToMany(Membership)

    def dollar_bills(self) -> LiteModel:
        return self.hasMany(DollarBill)

Membership.pivotsWith(Person, 'membership_person')