import unittest
from steer.schema import (
    Schema, ArrayProperty,
    IntegerProperty, StringProperty
)

# array without items
array_without_items = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
        "emails": {
            "type": "array"
        }
    }
}
# array of items defined in definitions
items_in_definitions = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
        "phones": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/phone"
            }
        }
    },
    "definitions": {
        "phone": {
            "type": "integer"
        }
    }
}

schema = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
        "phones": {
            "type": "array",
            "items": {
                "type": "integer"
            }
        },
        "emails": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}


class TestArrayProperty(unittest.TestCase):
    def setUp(self):
        self.schema = Schema.from_dict(schema)
        self.items_in_definitions = Schema.from_dict(items_in_definitions)
        self.array_without_items = Schema.from_dict(array_without_items)

    def test_integer_array_property(self):
        self.assertIsInstance(self.schema.properties[0], ArrayProperty)

        self.assertEqual(self.schema.properties[0].name, 'phones')
        self.assertIsInstance(self.schema.properties[0].items, IntegerProperty)

    def test_string_array_property(self):
        self.assertIsInstance(self.schema.properties[1], ArrayProperty)

        self.assertEqual(self.schema.properties[1].name, 'emails')
        self.assertIsInstance(self.schema.properties[1].items, StringProperty)

    def test_array_without_items(self):
        self.assertIsInstance(self.array_without_items.properties[0], ArrayProperty)
        self.assertEqual(self.array_without_items.properties[0].name, 'emails')
        self.assertIsNone(self.array_without_items.properties[0].items)

    def test_array_of_items_in_definitions(self):
        prop = self.items_in_definitions.properties[0]

        self.assertEqual(prop.name, 'phones')
        self.assertIsInstance(prop.items, IntegerProperty)
        self.assertEqual(prop.items.name, 'phone')


if __name__ == '__main__':
    unittest.main()
