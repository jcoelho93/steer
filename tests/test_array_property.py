import unittest
from steer.schema import (
    Schema, ArrayProperty,
    IntegerProperty, StringProperty
)


json_schema = {
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
        self.schema = Schema.from_dict(json_schema)

    def test_integer_array_property(self):
        self.assertIsInstance(self.schema.properties[0], ArrayProperty)

        self.assertEqual(self.schema.properties[0].name, 'phones')
        self.assertIsInstance(self.schema.properties[0].items, IntegerProperty)

    def test_string_array_property(self):
        self.assertIsInstance(self.schema.properties[1], ArrayProperty)

        self.assertEqual(self.schema.properties[1].name, 'emails')
        self.assertIsInstance(self.schema.properties[1].items, StringProperty)


if __name__ == '__main__':
    unittest.main()
