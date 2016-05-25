import unittest

from flask_restful_swagger_2 import Schema


class TestModel(Schema):
    """
    Test schema model.
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        }
    }
    required = ['id']


class SchemaTestCase(unittest.TestCase):
    def test_should_validate_schema_valid(self):
        self.assertEqual(TestModel(**{'id': 1, 'name': 'somebody'}),
                         {'id': 1, 'name': 'somebody'})

    def test_should_validate_schema_missing_required(self):
        with self.assertRaises(ValueError):
            TestModel(**{'name': 'somebody'})

    def test_should_validate_schema_invalid_type(self):
        with self.assertRaises(ValueError):
            TestModel(**{'id': '1'})
