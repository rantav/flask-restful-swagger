#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask
from flask_cors import CORS
from flask_restful_swagger_2 import swagger, get_swagger_blueprint

from views_blueprint import get_user_resources

app = Flask(__name__)
CORS(app)


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth

# A list of swagger document objects
docs = []

# Get user resources
user_resources = get_user_resources()

# Retrieve and save the swagger document object (do this for each set of resources).
docs.append(user_resources.get_swagger_doc())

# Register the blueprint for user resources
app.register_blueprint(user_resources.blueprint)

# Prepare a blueprint to server the combined list of swagger document objects and register it
app.register_blueprint(get_swagger_blueprint(docs, '/api/swagger', title='Example', api_version='1'))


@app.route('/')
def index():
    return """<head>
    <meta http-equiv="refresh" content="0; url=http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json" />
    </head>"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
