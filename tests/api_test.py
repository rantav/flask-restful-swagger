import unittest
import json

from flask import Flask
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


class TestResource(Resource):
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
    def get(self, user_id, _query):
        """
        Returns a specific user.
        :param user_id: The user identifier
        :param _query: Parsed query parameters
        """
        name = getattr(_query, 'name', 'somebody')
        return UserModel(**{'id': user_id, 'name': name}), 200


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(TestResource, '/users/<int:user_id>')
        self.app = app.test_client()

    def test_get_spec(self):
        # Retrieve spec
        r = self.app.get('/api/swagger.json')
        self.assertEqual(r.status_code, 200)

    def test_get_user(self):
        # Retrieve user
        r = self.app.get('/users/1?name=test')
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'test')
