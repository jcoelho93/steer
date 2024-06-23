import unittest
from steer.schema import Schema, ObjectProperty


schema = {
    "$schema": "https://example.com",
    "type": "object",
    "properties": {
        "securityRequirement": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
}


class TestAdditionalProperties(unittest.TestCase):
    def setUp(self):
        self.schema = Schema.from_dict(schema)

    def test_additional_properties(self):
        prop = self.schema.properties[0]

        self.assertEqual(prop.name, 'securityRequirement')
        self.assertIsInstance(prop, ObjectProperty)
        self.assertTrue(prop.additionalProperties)
        self.assertFalse(prop.properties)

    def test_prompt(self):
        pass


if __name__ == '__main__':
    unittest.main()
