# -*- coding: utf-8 -*-

from tests.apps import config
from flask import Flask
from flask.ext.restful import Api, Resource
from flask_restful_swagger import swagger

__author__ = 'sobolevn'

TODO_ITEM = 'test-item'


@swagger.model
class TodoItem:
    def __init__(self, arg1, arg2, arg3='123'):
        pass


class Todo(Resource):
    @swagger.operation(
        notes='get a todo item by ID',
        nickname='get',
        parameters=[{
            "name": "todo_id_x",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path",
        },{
            "name": "a_bool",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'boolean',
            "paramType": "path",
        }, ]
    )
    def get(self, todo_id):
        """Summary"""

        # We expect this method to be in our specs.
        return '{}{}'.format(TODO_ITEM, todo_id), 200, {
            'Access-Control-Allow-Origin': '*',
        }

    def options(self, **args):
        # We do not expect this method to be inside specs.
        return {
            'Allow': 'GET',
        }, 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        }


app = Flask(__name__, static_folder='../static')
app.config.from_object(config)

api_meta = {
    'apiVersion': '0.1',
    'resourcePath': '/',
    'produces': [
        'application/json',
        'text/html',
    ],
    'api_spec_url': '/api/spec',
    'description': 'A Basic API',
}

api = swagger.docs(Api(app), **api_meta)

api.add_resource(Todo, '/todo/<string:todo_id>')

if __name__ == '__main__':
    app.run()
