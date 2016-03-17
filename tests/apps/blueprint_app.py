# -*- coding: utf-8 -*-

from flask import Flask, Blueprint
from flask.ext.restful import Api
from flask_restful_swagger import swagger

from tests.apps import config
from tests.apps.shared_code import Todo, MarshalWithExample

__author__ = 'sobolevn'


api_meta_todo = {
    'apiVersion': '0.1',
    'resourcePath': '/',
    'produces': [
        'application/json',
        'text/html',
    ],
    'api_spec_url': '/api/spec',
    'description': 'A Basic Todo API',
}

api_meta_marshal = {
    'apiVersion': '0.1.2',
    'resourcePath': '/',
    'produces': [
        'application/json',
        'text/html',
    ],
    'api_spec_url': '/api/spec',
    'description': 'A Basic Marshal API',
}

app = Flask(__name__, static_folder='../static')
app.config.from_object(config)

todo_blueprint = Blueprint('todo_blueprint', __name__)
marshal_blueprint = Blueprint('marshal_blueprint', __name__)

api_todo = swagger.docs(Api(todo_blueprint), **api_meta_todo)
api_todo.add_resource(Todo, '/todo/<string:todo_id>')

api_marshal = swagger.docs(Api(marshal_blueprint), **api_meta_marshal)
api_marshal.add_resource(MarshalWithExample, '/marshal')

app.register_blueprint(todo_blueprint, url_prefix='/api-todo')
app.register_blueprint(marshal_blueprint, url_prefix='/api-marshal')

@app.route('/test')
def s():
    a = app
    return 'done'

if __name__ == '__main__':
    app.run()
