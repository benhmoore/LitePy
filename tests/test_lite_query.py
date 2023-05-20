import os
import glob
import unittest
from tests import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"


class TestLiteQuery(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Create a test database"""

        Lite.create_database(TEST_DB_PATH)
        Lite.connect(LiteConnection(database_path=TEST_DB_PATH))

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

    def tearDown(self):
        """Delete the Person and Pet"""
        self.person.delete()
        self.pet.delete()

        self.memberships.delete_all()

    def test_LiteQuery(self):
        # Remove all people
        Person.all().delete_all()

        # Create some test data
        person1 = Person.create({"name": "John", "age": 25})
        person2 = Person.create({"name": "Jane", "age": 30})
        person3 = Person.create({"name": "Billy", "age": 60})
        person4 = Person.create({"name": "Kendall", "age": 57})

        # Test the is_equal_to() method
        assert Person.where("age").is_equal_to(30).all() == [person2]

        # Test the is_not_equal_to() method
        assert Person.where("age").is_not_equal_to(30).all() == [
            person1,
            person3,
            person4,
        ]

        # Test the is_greater_than() method
        assert Person.where("age").is_greater_than(30).all() == [person3, person4]

        # Test the is_greater_than_or_equal_to() method
        assert Person.where("age").is_greater_than_or_equal_to(30).all() == [
            person2,
            person3,
            person4,
        ]

        # Test the is_less_than() method
        assert Person.where("age").is_less_than(60).all() == [person1, person2, person4]

        # Test the is_less_than_or_equal_to() method
        assert Person.where("age").is_less_than_or_equal_to(30).all() == [
            person1,
            person2,
        ]

        # Test the is_like() method
        assert Person.where("name").is_like("%il%").all() == [person3]

        # Test the is_not_like() method
        assert Person.where("name").is_not_like("%il%").all() == [
            person1,
            person2,
            person4,
        ]

        # Test the starts_with() method
        assert Person.where("name").starts_with("J").all() == [person1, person2]

        # Test the ends_with() method
        assert Person.where("name").ends_with("ll").all() == [person4]

        # Test the contains() method
        assert Person.where("name").contains("i").all() == [person3]

        # Test the or_where() method
        assert Person.where("name").is_equal_to("Billy").or_where("name").is_equal_to(
            "Kendall"
        ).all() == [person3, person4]

        # Test the and_where() method
        assert (
            Person.where("name")
            .is_equal_to("Billy")
            .and_where("name")
            .is_equal_to("Kendall")
            .all()
            == []
        )

    def test_complex_queries(self):
        # Remove all people
        Person.all().delete_all()

        # Create some test data
        person1 = Person.create({"name": "John", "age": 25})
        person2 = Person.create({"name": "Jane", "age": 30})
        person3 = Person.create({"name": "Billy", "age": 60})
        person4 = Person.create({"name": "Kendall", "age": 57})

        # Test that an appropriate exception is raised if the query is invalid
        with self.assertRaises(ValueError):
            query = (
                Person.where("age")
                .is_equal_to(25)
                .and_where("name LIKE 'J%'")
                .and_where("name = 'Billy'")
            )

        # Test that an appropriate exception is raised if the query returns no results
        query = Person.where("age").is_equal_to(100)
        with self.assertRaises(IndexError):
            query.first()
        with self.assertRaises(IndexError):
            query.last()
        assert query.all() == []
