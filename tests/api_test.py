import unittest
import json

from flask import Flask
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_2 import Api, Resource, Schema, swagger


class UserModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        }
    }
    required = ['name']


class ParseResource(Resource):
    @swagger.doc({
        'tags': ['user'],
        'description': 'Tests query parameter parser',
        'parameters': [
            {
                'name': 'str',
                'description': 'String value',
                'in': 'query',
                'type': 'string'
            },
            {
                'name': 'date',
                'description': 'Date value',
                'in': 'query',
                'type': 'string',
                'format': 'date'
            },
            {
                'name': 'datetime',
                'description': 'Date-time value',
                'in': 'query',
                'type': 'string',
                'format': 'date-time'
            },
            {
                'name': 'bool',
                'description': 'Boolean value',
                'in': 'query',
                'type': 'boolean'
            },
            {
                'name': 'int',
                'description': 'Integer value',
                'in': 'query',
                'type': 'integer'
            },
            {
                'name': 'float',
                'description': 'Float value',
                'in': 'query',
                'type': 'number',
                'format': 'float'
            }
        ],
        'responses': {
            '200': {
                'description': 'Parsed values'
            }
        }
     })
    def get(self, _parser):
        """
        Returns parsed query parameters.
        :param _parser: Query parameter parser
        """
        args = _parser.parse_args()

        return {
            'str': args.str,
            'date': args.date.isoformat(),
            'datetime': args.datetime.isoformat(),
            'bool': args.bool,
            'int': args.int,
            'float': args.float
        }, 200


class UserResource(Resource):
    @swagger.doc({
        'tags': ['user'],
        'description': 'Returns a user',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'User identifier',
                'in': 'path',
                'type': 'integer'
            },
            {
                'name': 'name',
                'description': 'User name',
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'User',
                'schema': UserModel,
                'examples': {
                    'application/json': {
                        'id': 1,
                        'name': 'somebody'
                    }
                }
            }
        }
     })
    def get(self, user_id, _parser):
        """
        Returns a specific user.
        :param user_id: The user identifier
        :param _parser: Query parameter parser
        """
        args = _parser.parse_args()

        name = args.get('name', 'somebody')
        return UserModel(**{'id': user_id, 'name': name}), 200


class EntityAddResource(Resource):
    post_parser = RequestParser()
    post_parser.add_argument('id', type=int, help='id help')
    post_parser.add_argument('name', type=str)
    post_parser.add_argument('value', type=float, default=1.1)
    post_parser.add_argument('private', type=bool, required=True)
    post_parser.add_argument('type', type=unicode, choices=['common', 'major', 'minor'])

    class PasswordType(str):
        swagger_type = 'password'
    post_parser.add_argument('password_arg', type=PasswordType, required=False)

    @swagger.doc({
        'tags': ['user'],
        'description': 'List of entities',
        'reqparser': {'name': 'EntityAddParser',
                      'parser': post_parser},
        'responses': {
            '200': {
                'description': 'User',
                'examples': {
                    'application/json': {
                        'id': 1,
                    }
                }
            }
        }
    })
    def post(self):
        """
        Returns a specific user.
        """
        args = self.post_parser.parse_args()

        name = args.get('name', 'somebody')
        return UserModel(**{'id': id, 'name': name}), 200


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        self.api = Api(app)
        self.api.add_resource(ParseResource, '/parse')
        self.api.add_resource(UserResource, '/users/<int:user_id>')
        self.app = app.test_client()
        self.context = app.test_request_context()

    def test_get_spec_object(self):
        # Retrieve spec object
        with self.context:
            spec = self.api.get_swagger_doc()
            self.assertTrue('info' in spec)
            self.assertTrue('paths' in spec)
            self.assertTrue('definitions' in spec)
            self.assertEqual(spec['swagger'], '2.0')

    def test_get_spec(self):
        # Retrieve spec
        r = self.app.get('/api/swagger.json')
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.data.decode('utf-8'))
        self.assertTrue('info' in data)
        self.assertTrue('paths' in data)
        self.assertTrue('definitions' in data)
        self.assertEqual(data['swagger'], '2.0')

    def test_parse_query_parameters(self):
        r = self.app.get('/parse?str=Test' +
                         '&date=2016-01-01' +
                         '&datetime=2016-01-01T12:00:00%2B00:00' +
                         '&bool=False' +
                         '&int=123' +
                         '&float=1.23')

        self.assertEqual(r.status_code, 200)

        data = json.loads(r.data.decode('utf-8'))
        self.assertEqual(data['str'], 'Test')
        self.assertEqual(data['date'], '2016-01-01T00:00:00')
        self.assertEqual(data['datetime'], '2016-01-01T12:00:00+00:00')
        self.assertEqual(data['bool'], False)
        self.assertEqual(data['int'], 123)
        self.assertEqual(data['float'], 1.23)

    def test_get_user(self):
        # Retrieve user
        r = self.app.get('/users/1?name=test')
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'test')


class TestFlaskSwaggerRequestParser(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        self.api = Api(app)
        self.api.add_resource(EntityAddResource, '/entities/')
        self.app = app.test_client()
        self.context = app.test_request_context()

    def test_request_parser_spec_definitions(self):
        # Retrieve spec
        r = self.app.get('/api/swagger.json')
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.data.decode('utf-8'))
        self.assertIn('definitions', data)
        self.assertIn('EntityAddParser', data['definitions'])
        self.assertEqual(data['definitions']['EntityAddParser']['type'], 'object')

        properties = data['definitions']['EntityAddParser']['properties']
        id_prop = properties.get('id')
        self.assertIsNotNone(id_prop)
        self.assertIsNone(id_prop['default'])
        self.assertFalse(id_prop['required'])
        self.assertEqual(id_prop['type'], 'integer')
        self.assertEqual(id_prop['name'], 'id')
        self.assertEqual(id_prop['description'], 'id help')

        name_prop = properties.get('name')
        self.assertIsNotNone(name_prop)
        self.assertIsNone(name_prop['default'])
        self.assertFalse(name_prop['required'])
        self.assertEqual(name_prop['type'], 'string')
        self.assertEqual(name_prop['name'], 'name')
        self.assertIsNone(name_prop['description'])

        priv_prop = properties.get('private')
        self.assertIsNotNone(priv_prop)
        self.assertIsNone(priv_prop['default'])
        self.assertTrue(priv_prop['required'])
        self.assertEqual(priv_prop['type'], 'boolean')
        self.assertEqual(priv_prop['name'], 'private')
        self.assertIsNone(priv_prop['description'])

        val_prop = properties.get('value')
        self.assertIsNotNone(val_prop)
        self.assertEqual(val_prop['default'], 1.1)
        self.assertFalse(val_prop['required'])
        self.assertEqual(val_prop['type'], 'float')
        self.assertEqual(val_prop['name'], 'value')
        self.assertIsNone(val_prop['description'])

        self.assertIsNotNone(properties.get('password_arg'))
        self.assertEqual(properties['password_arg']['type'], 'password')