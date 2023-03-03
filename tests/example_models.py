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

    table_name = "dollar_bills"

    def owner(self) -> LiteModel:
        return self.belongs_to(Person)

class Person(LiteModel):

    table_name = "people"

    def pets(self) -> LiteModel:
        return self.has_many(Pet)

    def brain(self) -> LiteModel:
        return self.has_one(Brain)

    def memberships(self) -> LiteModel:
        return self.belongs_to_many(Membership)

    def dollar_bills(self) -> LiteModel:
        return self.has_many(DollarBill)

Membership.pivots_with(Person, 'membership_person')

class Sibling(LiteModel):

    def siblings(self) -> LiteModel:
        return self.belongs_to_many(Sibling)

Sibling.pivots_with(Sibling, 'sibling_sibling')