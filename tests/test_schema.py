import unittest
from unittest import TestCase
from steer.schema import Schema, StringProperty, IntegerProperty, NumberProperty


schema_dict = {
    '$schema': "https://schema.test",
    'properties': {
        "name": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                }
            }
        }
    }
}


class TestSchema(TestCase):
    def test_loading_schema(self):
        schema = Schema.from_dict(schema_dict)

        self.assertEqual(schema.schema_url, schema_dict['$schema'])

    def test_string_property_enum(self):
        str_property: StringProperty = StringProperty.from_dict(
            "name",
            {
                'type': 'string',
                'format': 'email',
                'enum': ['a', 'b', 'c']
            },
            "$"
        )

        prompt_args = str_property._get_prompt_args()
        self.assertEqual(prompt_args['type'], 'select')

    def test_string_property(self):
        str_property: StringProperty = StringProperty.from_dict(
            "name",
            {
                'type': 'string',
                'format': 'email'
            },
            "$"
        )

        prompt_args = str_property._get_prompt_args()
        self.assertEqual(prompt_args['type'], 'input')

    def test_integer_numbers(self):
        int_property = IntegerProperty.from_dict(
            "integer",
            {
                'type': 'integer',
                'enum': [1, 2, 3]
            },
            "$"
        )
        with self.assertRaises(ValueError):
            int_property.set_value("4.2342")

        with self.assertRaises(ValueError):
            int_property.set_value("4")

    def test_numbers(self):
        number_property = NumberProperty.from_dict(
            "number",
            {
                'type': 'number',
                'enum': [1.321, 2, 3.0]
            },
            "$"
        )
        with self.assertRaises(ValueError):
            number_property.set_value("4.2342")

        try:
            number_property.set_value("2")
        except Exception:
            self.fail("Should not raise an exception")


if __name__ == '__main__':
    unittest.main()
