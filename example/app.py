#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.restful_swagger_2 import Api, swagger

from routes import routes

app = Flask(__name__)
CORS(app)
api = Api(app, api_version='0.1')


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth

for route in routes:
    api.add_resource(route[0], route[1])


@app.route('/')
def index():
    return """<head>
    <meta http-equiv="refresh" content="0; url=http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json" />
    </head>"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
