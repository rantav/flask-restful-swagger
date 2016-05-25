import unittest

import flask_restful_swagger_2.swagger as swagger
from flask_restful_swagger_2 import Schema


class TestModel(Schema):
    """
    Test schema model.
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'string'
        }
    }


class SwaggerTestCase(unittest.TestCase):
    def test_should_get_data_type_str(self):
        self.assertEqual(swagger.get_data_type({'type': 'string'}), str)

    def test_should_get_data_type_int(self):
        self.assertEqual(swagger.get_data_type({'type': 'integer'}), int)

    def test_should_get_data_type_bool(self):
        self.assertEqual(swagger.get_data_type({'type': 'boolean'}), bool)

    def test_should_get_data_type_list(self):
        self.assertEqual(swagger.get_data_type({'type': 'array'}), list)

    def test_should_get_data_type_float(self):
        self.assertEqual(swagger.get_data_type({'type': 'number', 'format': 'float'}), float)

    def test_should_get_data_type_double(self):
        self.assertEqual(swagger.get_data_type({'type': 'number', 'format': 'double'}), float)

    def test_should_get_data_type_invalid(self):
        self.assertEqual(swagger.get_data_type({}), None)

    def test_should_get_parser_arg(self):
        param = {
            'name': 'name',
            'description': 'Name to filter by',
            'type': 'string',
            'in': 'query'
        }

        expected = ('name', {
            'dest': 'name',
            'type': str,
            'location': 'args',
            'help': 'Name to filter by',
            'required': False,
            'default': None
        })

        self.assertEqual(swagger.get_parser_arg(param), expected)

    def test_should_get_parser_args(self):
        params = [
            {
                'name': 'body',
                'description': 'Request body',
                'in': 'body',
                'required': True,
            },
            {
                'name': 'name',
                'description': 'Name to filter by',
                'type': 'string',
                'in': 'query'
            }
        ]

        expected = [('name', {
            'dest': 'name',
            'type': str,
            'location': 'args',
            'help': 'Name to filter by',
            'required': False,
            'default': None
        })]

        self.assertEqual(swagger.get_parser_args(params), expected)

    def test_should_validate_path_item_object_invalid_field(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_path_item_object({'some_invalid_field': 1})

    def test_should_validate_operation_object_invalid_field(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_operation_object({'some_invalid_field': 1})

    def test_should_validate_operation_object_no_responses(self):
        obj = {
            'description': 'Returns all users',
            'parameters': [
                {
                    'name': 'name',
                    'description': 'Name to filter by',
                    'type': 'string',
                    'in': 'query'
                }
            ]
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_operation_object(obj)

    def test_should_validate_parameter_object_invalid_field(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object({'some_invalid_field': 1})

    def test_should_validate_parameter_object_no_name_field(self):
        obj = {
            'description': 'Name to filter by',
            'type': 'string',
            'in': 'query'
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_parameter_object_no_in_field(self):
        obj = {
            'name': 'name',
            'description': 'Name to filter by',
            'type': 'string',
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_parameter_object_invalid_in_field(self):
        obj = {
            'name': 'name',
            'description': 'Name to filter by',
            'type': 'string',
            'in': 'some_invalid_field'
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_parameter_object_body_no_schema(self):
        obj = {
            'name': 'name',
            'description': 'Name to filter by',
            'type': 'string',
            'in': 'body'
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_parameter_object_no_type_field(self):
        obj = {
            'name': 'name',
            'description': 'Name to filter by',
            'in': 'query'
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_parameter_object_array_no_items_field(self):
        obj = {
            'name': 'name',
            'description': 'Name to filter by',
            'type': 'array',
            'in': 'query',
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_parameter_object(obj)

    def test_should_validate_reference_object_no_ref_field(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_reference_object({})

    def test_should_validate_reference_object_multiple_keys(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_reference_object({'$ref': 1, 'other_field': 2})

    def test_should_validate_response_object_invalid_field(self):
        with self.assertRaises(swagger.ValidationError):
            swagger.validate_response_object({'some_invalid_field': 1})

    def test_should_validate_response_object_no_description(self):
        obj = {
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'name': 'somebody'
                    }
                ]
            }
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_response_object(obj)

    def test_should_validate_schema_object_required_not_list(self):
        obj = {
            "properties": {
                "id": {
                    "format": "int64",
                    "type": "integer"
                },
                "keys": {
                    "items": {
                        "$ref": "#/definitions/KeysModel"
                    },
                    "type": "array"
                },
                "mail": {
                    "$ref": "#/definitions/EmailModel"
                },
                "name": {
                    "type": "string"
                }
            },
            "required": "name",
            "type": "object"
        }

        with self.assertRaises(swagger.ValidationError):
            swagger.validate_schema_object(obj)

    def test_should_extract_swagger_path(self):
        self.assertEqual(swagger.extract_swagger_path('/path/<parameter>'), '/path/{parameter}')

    def test_should_extract_swagger_path_extended(self):
        self.assertEqual(swagger.extract_swagger_path('/<string(length=2):lang_code>/<string:id>/<float:probability>'),
                         '/{lang_code}/{id}/{probability}')

    def test_should_sanitize_doc(self):
        self.assertEqual(swagger.sanitize_doc('line1\nline2\nline3'), 'line1<br/>line2<br/>line3')

    def test_should_sanitize_doc_multi_line(self):
        self.assertEqual(swagger.sanitize_doc(['line1\nline2', None, 'line3\nline4']),
                         'line1<br/>line2<br/>line3<br/>line4')

    def test_should_parse_method_doc(self):
        def test_func(a):
            """
            Test function
            :param a: argument
            :return: Nothing
            """

        self.assertEqual(swagger.parse_method_doc(test_func, {}), 'Test function')

    def test_should_parse_method_doc_append_summary(self):
        def test_func(a):
            """
            Test function
            :param a: argument
            :return: Nothing
            """

        self.assertEqual(swagger.parse_method_doc(test_func, {'summary': 'Summary'}),
                         'Summary<br/>Test function')

    def test_should_parse_schema_doc(self):
        test_model = TestModel()
        self.assertEqual(swagger.parse_schema_doc(test_model, {}), 'Test schema model.')

    def test_should_parse_schema_doc_existing_description(self):
        test_model = TestModel()
        self.assertIsNone(swagger.parse_schema_doc(test_model,
                                                   {'description': 'Test description'}))
