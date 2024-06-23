import unittest
from steer.schema import (
    Schema, ObjectProperty, StringProperty,
    IntegerProperty, NumberProperty, BooleanProperty,
    ArrayProperty
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
        },
        "multipleOf": {
            "$ref": "https://json-schema.org/draft-04/schema#/properties/multipleOf"
        },
        "enum": {
            "$ref": "https://json-schema.org/draft-04/schema#/properties/enum"
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

array_of_ref = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
       "security": {
           "type": "array",
           "items": {
               "$ref": "#/definitions/securityRequirement"
           }
       }
    },
    "definitions": {
        "securityRequirement": {
            "type": "object",
            "properties": {
                "authentication": {
                    "type": "string"
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

    def test_url_reference_property(self):
        prop = self.schema.properties[5]

        self.assertEqual(prop.name, 'multipleOf')
        self.assertEqual(prop.type, 'number')

    def test_array_of_reference_property(self):
        schema = Schema.from_dict(array_of_ref)

        prop = schema.properties[0]

        self.assertEqual(prop.name, 'security')
        self.assertEqual(prop.type, 'array')
        self.assertIsInstance(prop, ArrayProperty)
        self.assertIsInstance(prop.items, ObjectProperty)


if __name__ == '__main__':
    unittest.main()
