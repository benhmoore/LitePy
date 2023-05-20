import os
import glob
import unittest
from tests import *

# Define the database path for the test database
TEST_DB_PATH = "test.sqlite"


class TestLiteCollection(unittest.TestCase):
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

        # Create Dollar Bill table
        LiteTable.create_table(
            "dollar_bills",
            {"owner_id": "INTEGER", "name": "TEXT"},
            {"owner_id": ("people", "id")},
        )

    @classmethod
    def tearDownClass(self):
        """Delete the test database"""

        Lite.disconnect()

        # remove test database
        for file_name in glob.glob("*.sqlite*"):
            os.remove(file_name)

    def setUp(self):
        self.person1 = Person.create({"name": "John Smith"})

        self.person2 = Person.create({"name": "Jane Smith"})

        self.person3 = Person.create({"name": "Jack Smith"})

        self.dollar_bills = LiteCollection(
            [DollarBill.create({"name": n}) for n in range(4)]
        )

    def tearDown(self):
        self.person1.delete()
        self.person2.delete()
        self.person3.delete()

        self.dollar_bills.delete_all()

    def test_add(self):
        collection = LiteCollection()
        collection.add(self.person1)

        assert len(collection) == 1
        assert collection[0] == self.person1

        # Test adding a duplicate
        with self.assertRaises(DuplicateModelInstance):
            collection = collection + self.person1
        with self.assertRaises(DuplicateModelInstance):
            collection.add(self.person1)

        # Test adding incompatible model type to existing collection
        with self.assertRaises(TypeError):
            collection.add(Pet.create({"name": "Fido"}))

    def test_attach_to_all(self):
        self.dollar_bills.attach_to_all(self.person1)

        assert len(self.person1.dollar_bills()) == 4
        assert len(self.person2.dollar_bills()) == 0

    def test_detach_from_all(self):
        self.dollar_bills.attach_to_all(self.person1)
        self.dollar_bills.detach_from_all(self.person1)

        assert len(self.person1.dollar_bills()) == 0

    def test_detach_many_from_all(self):
        self.dollar_bills.attach_to_all(self.person1)
        self.dollar_bills.detach_many_from_all([self.person1])

        assert len(self.person1.dollar_bills()) == 0

    def test_attach_many_to_all(self):
        self.dollar_bills
        with self.assertRaises(RelationshipError):
            self.dollar_bills.attach_many_to_all([self.person1, self.person2])

    def test_first(self):
        collection = LiteCollection([self.person1, self.person2])

        assert collection.first() == self.person1

        collection = LiteCollection([self.person1, self.person2])

        assert collection.last() == self.person2

    def test_intersection(self):
        collection1 = LiteCollection([self.person1, self.person2])
        collection2 = LiteCollection([self.person2, self.person3])

        intersection = collection1.intersection(collection2)

        assert len(intersection) == 1
        assert intersection[0] == self.person2

    def test_difference(self):
        collection1 = LiteCollection([self.person1, self.person2])
        collection2 = LiteCollection([self.person2, self.person3])

        difference = collection1.difference(collection2)

        assert len(difference) == 1
        assert difference[0] == self.person1

    def test_where(self):
        # Create some data to query
        person1 = Person.create({"name": "Alice", "age": 25})

        person2 = Person.create({"name": "Bob", "age": 30})

        person3 = Person.create({"name": "Axel", "age": 3})

        person4 = Person.create({"name": "Toby", "age": 55})

        person5 = Person.create({"name": "Rex", "age": 42})

        collection = LiteCollection([person1, person2, person3, person4, person5])

        # Query for results with name "Alice"
        results = collection.where("name").is_equal_to("Alice").all()
        assert len(results) == 1
        assert results[0].name == "Alice"

        # Query for results with age less than 3
        results = collection.where("age").is_less_than(4).all()
        assert len(results) == 1
        assert results[0].name == "Axel"

        # Query for results with age greater than or equal to 3
        results = collection.where("age").is_greater_than_or_equal_to(4).all()
        assert len(results) == 4
        assert [result.name for result in results] == ["Alice", "Bob", "Toby", "Rex"]

        # Query for results with age not equal to 30
        results = collection.where("age").is_not_equal_to(30).all()
        assert len(results) == 4
        assert person2 not in results

        # Query for results with name containing "u"
        results = collection.where("name").contains("x").all()
        assert len(results) == 2

        # Query for results with name not containing "u"
        results = collection.where("name").does_not_contain("x").all()
        assert len(results) == 3

        # Query for results with age less than or equal to 25
        results = collection.where("age").is_less_than_or_equal_to(25).all()
        assert len(results) == 2

        # Query for results with age greater than 25
        results = collection.where("age").is_greater_than(25).all()
        assert len(results) == 3

        # Test sorting
        result = collection.sort("age").first()
        self.assertEqual(result, person3)  # Fluffy is the youngest

        # Test sorting in reverse
        result = collection.sort("age", reverse=True).first()
        self.assertEqual(result, person4)  # Bob is the oldest

        # Test sorting by id
        result = collection.sort().last()
        self.assertEqual(result, person5)  # Bob should have highest id

        # Clean up
        person1.delete()
        person2.delete()
        person3.delete()
        person4.delete()
        person5.delete()

    def test_fresh(self):
        person1 = Person.create({"name": "John Smith"})

        collection = LiteCollection([person1])
        person1.name = "Mike"
        person1.save()
        collection.fresh()

        assert len(collection) == 1
        assert collection[0].name == "Mike"

        person1.delete()

    def test_delete_all(self):
        all_people = Person.all()
        all_people.delete_all()

        assert len(Person.all()) == 0

    def test_model_keys(self):
        # Create some test data
        person1 = Person.create({"name": "Alice", "age": 25})

        person2 = Person.create({"name": "Bob", "age": 30})

        collection = LiteCollection([person1, person2])

        # Check that the keys are returned correctly
        assert collection.model_keys() == [person1.id, person2.id]

        # Clean up
        person1.delete()
        person2.delete()

    def test_join(self):
        person1 = Person.create({"name": "Alice", "age": 25})

        person2 = Person.create({"name": "Bob", "age": 30})

        collection1 = LiteCollection([person1])
        collection2 = LiteCollection([person2])

        collection1.join(collection2)

        assert len(collection1) == 2
        assert collection1[1] == person2

        person1.delete()
        person2.delete()

    def test_remove(self):
        person1 = Person.create({"name": "Alice", "age": 25})

        person2 = Person.create({"name": "Bob", "age": 30})

        collection = LiteCollection([person1, person2])

        collection.remove(person1)

        assert len(collection) == 1
        assert person1 not in collection

        with self.assertRaises(ModelInstanceNotFoundError):
            collection.remove(person1)

        person1.delete()
        person2.delete()

    def test_str(self):
        person1 = Person.create({"name": "John Smith"})

        person2 = Person.create({"name": "Jane Smith"})

        collection = LiteCollection([person1, person2])

        expected_output = [person1.to_dict(), person2.to_dict()].__str__()
        assert collection.__str__() == expected_output

        person1.delete()
        person2.delete()

    def test_operator_overloads(self):
        person1 = Person.create({"name": "Alice", "age": 25})

        person2 = Person.create({"name": "Bob", "age": 30})

        person3 = Person.create({"name": "Charlie", "age": 35})

        person4 = Person.create({"name": "Dave", "age": 40})

        collection1 = LiteCollection([person1, person2])
        collection2 = LiteCollection([person3, person4])
        collection3 = LiteCollection(self.dollar_bills)

        # Test attempting to add incompatible types
        with self.assertRaises(TypeError):
            collection3 = collection3 + collection1

        assert collection1.__repr__() == str(collection1.list)

        # Test __add__ overload
        # Test adding two collections
        collection3 = collection1 + collection2
        print(collection3)
        assert len(collection3) == 4
        assert person1 in collection3
        assert person2 in collection3
        assert person3 in collection3
        assert person4 in collection3

        # Test adding a collection and a model
        collection4 = collection1 + person3
        assert len(collection4) == 3
        assert person1 in collection4
        assert person2 in collection4
        assert person3 in collection4

        # Test adding a list to a collection
        collection5 = collection1 + [person3, person4]
        assert len(collection5) == 4

        # Test __len__ overload
        assert len(collection1) == 2

        # Test __eq__ overload
        collection5 = LiteCollection([person1, person2])
        assert collection1 == collection5

        assert collection1 == [person1, person2]

        # Test __contains__ overload
        assert person1 in collection1
        assert person3 not in collection1

        model_id = collection1[0].id
        assert model_id in collection1

        # Test __getitem__ overload
        assert collection1[0] == person1

        # Clean up
        person1.delete()
        person2.delete()
        person3.delete()
        person4.delete()
