import unittest
from steer.schema import (
    Schema, ObjectProperty, StringProperty,
    IntegerProperty, NumberProperty, BooleanProperty
)


json_schema = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
        "name": {
            "$ref": "#/definitions/name"
        },
        "age": {
            "$ref": "#/definitions/age"
        },
        "net_worth": {
            "$ref": "#/definitions/net_worth"
        },
        "married": {
            "$ref": "#/definitions/married"
        },
        "address": {
            "$ref": "#/definitions/address"
        }
    },
    "definitions": {
        "name": {
            "type": "string",
            "pattern": "^[A-Z]+$"
        },
        "age": {
            "type": "integer"
        },
        "net_worth": {
            "type": "number"
        },
        "married": {
            "type": "boolean"
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                },
                "postal_code": {
                    "type": "string",
                    "pattern": "^[0-9]{4}-[0-9]{3}$"
                }
            }
        }
    }
}


class TestRefProperty(unittest.TestCase):
    def setUp(self):
        self.schema = Schema.from_dict(json_schema)

    def test_loading_definitions(self):
        self.assertIsInstance(self.schema.definitions[0], StringProperty)
        self.assertIsInstance(self.schema.definitions[1], IntegerProperty)
        self.assertIsInstance(self.schema.definitions[2], NumberProperty)
        self.assertIsInstance(self.schema.definitions[3], BooleanProperty)
        self.assertIsInstance(self.schema.definitions[4], ObjectProperty)

    def test_referenced_object_fields(self):
        prop = self.schema.properties[4]

        self.assertEqual(prop.name, 'address')
        self.assertEqual(prop.type, 'object')
        for p in prop.properties:
            self.assertIsInstance(p, StringProperty)


if __name__ == '__main__':
    unittest.main()
