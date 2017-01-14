#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask
from flask_cors import CORS
from flask_restful_swagger_2 import Api, swagger

from views import UserResource, UserItemResource

app = Flask(__name__)
CORS(app)
api = Api(app, api_version='0.1')


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth

api.add_resource(UserResource, '/api/users')
api.add_resource(UserItemResource, '/api/users/<int:user_id>')


@app.route('/')
def index():
    return """<head>
    <meta http-equiv="refresh" content="0; url=http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json" />
    </head>"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
