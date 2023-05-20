import os
import glob
import unittest
from tests import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"


class Car(LiteModel):
    DEFAULT_CONNECTION = None

    def owner(self) -> LiteModel:
        return self.belongs_to(Person)


class TestLiteModel(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Create a test database"""

        Lite.create_database(TEST_DB_PATH)
        Lite.connect(LiteConnection(database_path=TEST_DB_PATH))

        # Test models with default connections specified
        Lite.create_database("additional.sqlite")
        Car.DEFAULT_CONNECTION = LiteConnection(database_path="additional.sqlite")

        # Create Car table
        LiteTable.create_table(
            "cars",
            {"name": "TEXT", "owner_id": "INTEGER"},
            {"owner_id": ("people", "id")},
            Car.DEFAULT_CONNECTION,
        )

        # Create Pet table
        Pet.requires_table(
            {"name": "TEXT", "age": "INTEGER", "owner_id": "INTEGER"},
            {"owner_id": ("people", "id")},
        )

        # Create Brain table
        LiteTable.create_table(
            "brains",
            {"name": "TEXT", "person_id": "INTEGER"},
            {"person_id": ("people", "id")},
        )

        # Create Person table
        LiteTable.create_table(
            "people",
            {
                "name": "TEXT",
                "age": "INTEGER",
            },
        )

        # Create Person table
        LiteTable.create_table(
            "memberships",
            {
                "name": "TEXT",
            },
        )

        # Create Dollar Bill table
        LiteTable.create_table(
            "dollar_bills",
            {"owner_id": "INTEGER", "name": "TEXT"},
            {"owner_id": ("people", "id")},
        )

        LiteTable.create_table(
            "membership_person",
            {
                "person_id": "INTEGER",
                "membership_id": "INTEGER",
            },
            {"person_id": ["people", "id"], "membership_id": ["memberships", "id"]},
        )

        LiteTable.create_table(
            "siblings",
            {
                "name": "TEXT",
            },
        )

        LiteTable.create_table(
            "sibling_sibling",
            {
                "sibling_1_id": "INTEGER",
                "sibling_2_id": "INTEGER",
            },
            {
                "sibling_1_id": ["siblings", "id"],
                "sibling_2_id": ["siblings", "id"],
            },
        )

    @classmethod
    def tearDownClass(self):
        """Delete the test database"""
        Lite.disconnect()

        # remove test database
        for file_name in glob.glob("*.sqlite*"):
            os.remove(file_name)

    def setUp(self):
        """Create a new Person and Pet"""
        self.person = Person.create({"name": "John", "age": 25})

        self.pet = Pet.create(
            {
                "name": "Fido",
                "age": 3,
            }
        )

        self.memberships = Membership.create_many(
            [
                {"name": "membership1"},
                {"name": "membership2"},
            ]
        )

        Car.create({"name": "car1"})

    def tearDown(self):
        """Delete the Person and Pet"""
        self.person.delete()
        self.pet.delete()

        self.memberships.delete_all()

    def test_create(self):
        """Test LiteModel creation"""
        self.assertEqual(self.person.name, "John")
        self.assertEqual(self.person.age, 25)

        self.assertEqual(self.pet.name, "Fido")
        self.assertEqual(self.pet.age, 3)

        # Create a new person using the initializer
        george = Person()
        george.name = "George"
        george.age = 42
        george.save()

        # Check that the person was created
        person = Person.find_or_fail(george.id)
        self.assertEqual(person.name, "George")

        george.delete()

        # Check that the person was deleted
        self.assertRaises(ModelInstanceNotFoundError, Person.find_or_fail, person.id)

    def test_str(self):
        # create a new instance of a model
        person = Person.create({"name": "John", "age": 25})

        assert "'name': 'John'" in str(person)

        person.delete()

    def test_repr(self):
        # create a new instance of a model
        person = Person.create({"name": "John", "age": 30})

        # check that the string representation of the model is correct
        assert "'John', 30" in repr(person)

    def test_lt(self):
        person2 = Person.create({"name": "John", "age": 30})
        assert self.person < person2
        with self.assertRaises(TypeError):
            assert self.person < 1

    def test_belongs_to_many(self):
        """Test the belongs_to_many() method"""

        # Attach the membership to the person
        self.memberships.attach_to_all(self.person)

        # Check that the person's memberships are the membership
        self.assertEqual(self.person.memberships()[0].id, self.memberships[0].id)

    def test_belongs_to(self):
        """Test the belongs_to() method"""

        # Attach the pet to the person
        self.pet.attach(self.person)

        # Check that the pet's owner is the person
        self.assertEqual(self.pet.owner().id, self.person.id)

    def test_has_many(self):
        """Test the has_many() method"""

        # Attach the pet to the person
        self.pet.attach(self.person)

        # Check that the person's pets are the pet
        self.assertEqual(self.person.pets()[0].id, self.pet.id)

    def test_has_one(self):
        """Test the has_one() method"""

        # Attach the brain to the person
        brain = Brain.create(
            {
                "name": "Brain",
            }
        )
        brain.attach(self.person)

        # Check that the person's brain is the brain
        self.assertEqual(self.person.brain().id, brain.id)
        self.assertEqual(brain.owner().id, self.person.id)

    def test_find_or_fail(self):
        """Test the find_or_fail() method"""

        # Check that the person can be found
        self.assertEqual(Person.find_or_fail(self.person.id).id, self.person.id)

        # Check that an exception is raised if the person can't be found
        with self.assertRaises(ModelInstanceNotFoundError):
            Person.find_or_fail(100)

    def test_find(self):
        """Test the find() method"""

        # Check that the person can be found
        self.assertEqual(Person.find(self.person.id).id, self.person.id)

        # Check that None is returned if the person can't be found
        self.assertIsNone(Person.find(100))

    def test_attach_detach(self):
        """Test the attach() method"""

        membership42 = Membership.create({"name": "membership42"})

        # Attach the person to the membership
        membership42.attach(self.person)

        # Check that the person's memberships are the membership
        self.assertEqual(self.person.memberships()[0].id, membership42.id)
        self.assertEqual(membership42.people()[0].id, self.person.id)

        membership42.detach(self.person)

        # Attach the membership to the person
        self.person.attach(membership42)

        # Check that the person's memberships are the membership
        self.assertEqual(self.person.memberships()[0].id, membership42.id)
        self.assertEqual(membership42.people()[0].id, self.person.id)

        # Attach person to brain
        brain1 = Brain.create({"name": "brain1"})
        self.person.attach(brain1)

        # Try tests that should fail
        with self.assertRaises(TypeError):
            self.person.attach(1)

        with self.assertRaises(RelationshipError):
            self.person.attach(self.person)

        with self.assertRaises(RelationshipError):
            self.person.attach_many([self.person])

        with self.assertRaises(RelationshipError):
            self.person.attach_many([membership42])

        self.person.detach(membership42)
        with self.assertRaises(RelationshipError):
            self.person.detach(membership42)

        with self.assertRaises(TypeError):
            self.person.detach(1)

        with self.assertRaises(RelationshipError):
            brain1 = Brain.create({"name": "brain1"})
            brain1.attach(self.person)

            # This should fail
            brain1.attach(self.person)
            self.person.attach(brain1)

        with self.assertRaises(RelationshipError):
            brain1 = Brain.create({"name": "brain1"})
            brain1.attach(self.person)

            # This should fail
            self.person.attach(brain1)

        with self.assertRaises(RelationshipError):
            brain1 = Brain.create({"name": "brain1"})
            brain1.attach(self.person)

            # This should fail
            self.person.detach(brain1)
            brain1.detach(self.person)

        with self.assertRaises(RelationshipError):
            brain1 = Brain.create({"name": "brain1"})
            brain1.attach(self.person)

            # This should fail
            brain1.detach(self.person)
            self.person.detach(brain1)

    def test_pivot_with_self(self):
        """Test many-to-many relationships within the same model"""

        sibling1 = Sibling.create({"name": "sibling1"})
        sibling2 = Sibling.create({"name": "sibling2"})

        sibling1.attach(sibling2)

        self.assertEqual(sibling1.siblings().first(), sibling2)

    def test_all(self):
        """Test the all() method"""

        person2 = Person.create({"name": "Jane", "age": 30})

        # Check that all people are returned
        self.assertEqual(len(Person.all()), 2)

        person2.delete()

        self.car = Car(1)
        self.car = Car.all()[0]

    def test_where(self):
        """Test the where() method"""

        person2 = Person.create({"name": "Jane", "age": 30})
        person3 = Person.create({"name": "Billy", "age": 60})
        person4 = Person.create({"name": "Kendall", "age": 57})

        # Check that the correct person is returned
        assert Person.where("age").is_greater_than(30).all() == [person3, person4]
        assert Person.where("age").is_greater_than_or_equal_to(31).all() == [
            person3,
            person4,
        ]
        assert Person.where("age").is_greater_than_or_equal_to(31).and_where(
            "age"
        ).is_less_than(60).all() == [person4]
        assert Person.where("age").is_greater_than_or_equal_to(31).and_where(
            "age"
        ).is_less_than(60).and_where("name").contains("end").all() == [person4]

        self.assertEqual(Person.where("name").is_equal_to("Jane").last().id, person2.id)

        person2.delete()

        self.car = Car.where("name").is_equal_to("car1").all()[0]

        assert self.car.name == "car1"

    def test_create_many(self):
        """Test the create_many() method"""

        # Create two pets
        new_pets = Pet.create_many(
            [
                {"name": "Tulip", "age": 3},
                {"name": "Spot", "age": 5},
            ]
        )

        # Check that the pets were created
        self.assertEqual(len(Pet.all()), 3)

        # Delete the pets
        new_pets.delete_all()
        assert len(Pet.all()) == 1

    # def test_values(self):
    #     self.person.age = [{"value": 30, "unit": "years"}]
    #     self.person.save()
    #     self.person.fresh()
    #     print(self.person)
    #     assert 1 == 2

    def test_manyToMany(self):
        """Test the manyToMany() method"""

        # Attach the person to the memberships
        self.person.attach_many(self.memberships)

        # Check that the person's memberships are the memberships
        self.assertEqual(len(self.person.memberships()), 2)

        person2 = Person.create({"name": "Jane", "age": 30})

        # Attach the person to the first membership
        person2.attach(self.memberships[0])

        # Check that the memberships' people are the person
        self.assertEqual(len(self.memberships[0].people()), 2)

        # Detach the person from the first membership
        self.memberships[0].detach(person2)
        self.assertEqual(len(self.memberships[0].people()), 1)

        # Detach the person from the memberships
        self.person.detach_many(self.memberships)
        self.assertEqual(len(self.person.memberships()), 0)
        person2.delete()

    def test_save(self):
        """Test the save() method"""

        # Change the person's name
        self.person.name = "Ben"

        # Save the person
        self.person.save()

        # Check that the person's name was changed
        self.assertEqual(Person.find(self.person.id).name, "Ben")

    def test_fresh(self):
        """Test the fresh() method"""

        # Change the person's name
        self.person.name = "Ben"

        # Check that the person's name hasn't changed
        self.person.fresh()
        self.assertEqual(self.person.name, "John")

    def test_find_path(self):
        """Test the find_path() method"""

        # Set up people and attach to membership
        person2 = Person.create({"name": "Jane", "age": 30})
        self.memberships[0].attach_many([self.person, person2])
        person2.attach(self.memberships[1])

        assert len(self.person.find_path(person2)) == 3
        assert len(person2.find_path(self.person)) == 3
        assert len(person2.find_path(self.pet)) == 0

        person2.delete()

    def test_accessed_through(self):
        """Test the accessed_through() method"""

        Lite.create_database("accessed_through.sqlite")
        conn = LiteConnection("accessed_through.sqlite")

        LiteTable.create_table("computers", {"name": "text"}, {}, lite_connection=conn)

        LiteTable.create_table(
            "users_computers",
            {"user_id": "integer", "computer_id": "integer"},
            {"user_id": ("people", "id"), "computer_id": ("computers", "id")},
        )

        class UserOfComputer(Person):
            def computers(self) -> LiteModel:
                return self.belongs_to_many(Computer)

        class Computer(LiteModel):
            def users(self) -> LiteModel:
                return self.belongs_to_many(UserOfComputer)

        Computer.accessed_through(lite_connection=conn)
        Computer.pivots_with(UserOfComputer, "users_computers")

        user1 = UserOfComputer.create({"name": "John", "age": 20})

        computer1 = Computer.create({"name": "computer1"})

        user1.attach(computer1)
        self.assertEqual(LiteCollection([computer1]), user1.computers())

        user1.delete()
        computer1.delete()

    def test_delete(self):
        """Test the delete() method"""

        # Create and delete brain
        brain1 = Brain.create({"name": "brain1"})
        brain1.delete()

        # Test that brain was deleted
        self.assertEqual(brain1.id, None)

        # Try to delete brain again
        self.assertRaises(ModelInstanceNotFoundError, brain1.delete)

    def test_print(self):
        """Test various printing various variants of a LiteModel"""

        # Test representing a LiteModel with bytes as a string
        bt = b"Hello, world!"
        self.person.name = bt
        self.assertIn("Hello, world!", str(self.person))

        # Test representing a LiteModel with a string longer than 50 characters
        self.person.name = "Hello, world! Hello, world! Hello, world! Hello, world!"
        self.assertIn(
            "Hello, world! Hello, world! Hello, world! Hello, w...", str(self.person)
        )
