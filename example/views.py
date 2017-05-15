from flask import request
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_2 import swagger, Resource

from models import UserModel, ErrorModel


known_users = []


class UserResource(Resource):
    @swagger.doc({
        'tags': ['users'],
        'description': 'Adds a user',
        'parameters': [
            {
                'name': 'body',
                'description': 'Request body',
                'in': 'body',
                'schema': UserModel,
                'required': True,
            }
        ],
        'responses': {
            '201': {
                'description': 'Created user',
                'schema': UserModel,
                'headers': {
                    'Location': {
                        'type': 'string',
                        'description': 'Location of the new item'
                    }
                },
                'examples': {
                    'application/json': {
                        'id': 1
                    }
                }
            }
        }
    })
    def post(self):
        """
        Adds a user.
        """
        # Validate request body with schema model
        try:
            data = UserModel(**request.get_json())

        except ValueError as e:
            return ErrorModel(**{'message': e.args[0]}), 400

        data['id'] = len(known_users) + 1
        known_users.append(data)

        return data, 201, {'Location': request.path + '/' + str(data['id'])}

    @swagger.doc({
        'tags': ['users'],
        'description': 'Returns all users',
        'parameters': [
            {
                'name': 'name',
                'description': 'Name to filter by',
                'type': 'string',
                'in': 'query'
            }
        ],
        'responses': {
            '200': {
                'description': 'List of users',
                'schema': UserModel,
                'examples': {
                    'application/json': [
                        {
                            'id': 1,
                            'name': 'somebody'
                        }
                    ]
                }
            }
        }
    })
    def get(self, _parser):
        """
        Returns all users.
        :param _parser: Query parameter parser
        """
        # swagger.doc decorator returns a query parameter parser in the special
        # '_parser' function argument if it is present
        args = _parser.parse_args()

        users = ([u for u in known_users if u['name'] == args['name']]
                 if 'name' in args else known_users)

        # Return data through schema model
        return map(lambda user: UserModel(**user), users), 200


class UserItemResource(Resource):
    @swagger.doc({
        'tags': ['user'],
        'description': 'Returns a user',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'User identifier',
                'in': 'path',
                'type': 'integer'
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
    def get(self, user_id):
        """
        Returns a specific user.
        :param user_id: The user identifier
        """
        user = next((u for u in known_users if u['id'] == user_id), None)

        if user is None:
            return ErrorModel(**{'message': "User id {} not found".format(user_id)}), 404

        # Return data through schema model
        return UserModel(**user), 200


class GroupResource(Resource):
    post_parser = RequestParser()
    post_parser.add_argument('name', type=str, required=True)
    post_parser.add_argument('id', type=int, help='Id of new group')
    post_parser.add_argument('type', type=str, choices=['first', 'second', 'third'])
    added_groups = []

    @swagger.doc({
        'tags': ['groups'],
        'description': 'Adds a group',
        'reqparser': {'name': 'GroupsModel',
                      'parser': post_parser},
        'responses': {
            '201': {
                'description': 'Created group',
                'examples': {
                    'application/json': {
                        'id': 1
                    }
                }
            }
        }
    })
    def post(self):
        """
        Creates group
        """
        args = self.post_parser.parse_args()
        new_group = {'name': args['name'], 'id': len(self.added_groups) + 1}
        self.added_groups.append(new_group)

        return new_group, 201
