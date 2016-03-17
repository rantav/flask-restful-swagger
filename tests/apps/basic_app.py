# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.restful import Api
from flask_restful_swagger import swagger

from tests.apps import config
from tests.apps.shared_code import Todo, MarshalWithExample

__author__ = 'sobolevn'


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

app = Flask(__name__, static_folder='../static')
app.config.from_object(config)

api = swagger.docs(Api(app), **api_meta)
api.add_resource(Todo, '/todo/<string:todo_id>')
api.add_resource(MarshalWithExample, '/marshal')

if __name__ == '__main__':
    app.run()
