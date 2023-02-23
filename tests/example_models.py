from lite import *

class Pet(LiteModel):

    def owner(self) -> LiteModel:
        return self.belongs_to(Person)

class Brain(LiteModel):

    def owner(self) -> LiteModel:
        return self.belongs_to(Person)

class Membership(LiteModel):
    
    def people(self) -> LiteModel:
        return self.belongs_to_many(Person)

class DollarBill(LiteModel):

    TABLE_NAME = "dollar_bills"

    def owner(self) -> LiteModel:
        return self.belongs_to(Person)

class Person(LiteModel):

    TABLE_NAME = "people"

    def pets(self) -> LiteModel:
        return self.has_many(Pet)

    def brain(self) -> LiteModel:
        return self.has_one(Brain)

    def memberships(self) -> LiteModel:
        return self.belongs_to_many(Membership)

    def dollar_bills(self) -> LiteModel:
        return self.has_many(DollarBill)

Membership.pivots_with(Person, 'membership_person')