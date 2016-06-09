# flask-restful-swagger-2.0

[![Build Status](https://travis-ci.org/swege/flask-restful-swagger-2.0.svg?branch=master)](https://travis-ci.org/swege/flask-restful-swagger-2.0)

## What is flask-restful-swagger-2?

flask-restful-swagger-2 is a wrapper for [flask-restful](http://flask-restful.readthedocs.org/en/latest/) which
enables [swagger](http://swagger.io/) support according to the [swagger 2.0 specification](http://swagger.io/specification/).

This project is based on [flask-restful-swagger](https://github.com/rantav/flask-restful-swagger), but it only
supported swagger 1.2.

## Getting started

Install:

```
pip install flask-restful-swagger-2
```

To use it, change your import from `from flask.ext.restful import Api` to `from flask.ext.restful_swagger_2 import Api`.

```python
from flask import Flask
# Instead of using this: from flask.ext.restful import  Api
# Use this:
from flask.ext.restful_swagger_2 import Api

app = Flask(__name__)

# Use the swagger Api class as you would use the flask restful class.
# It supports several (optional) parameters, these are the defaults:
api = Api(app, api_version='0.0', api_spec_url='/api/swagger')
```

The Api class supports the following parameters:

| Parameter | Description |
| --------- | ----------- |
| `api_version` | The API version string (defaults to '0.0'). Maps to the `version` field of the [info object](http://swagger.io/specification/#infoObject). |
| `api_spec_url` | The URL path that serves the swagger specification document (defaults to `/api/swagger`). |
| `base_path` | The base path on which the API is served. Maps to the `basePath` field of the [schema object](http://swagger.io/specification/#schemaObject). |
| `consumes` | A list of MIME types the API can consume. Maps to the `consumes` field of the [schema object](http://swagger.io/specification/#schemaObject). |
| `contact` | The contact information for the API. Maps to the `contact` field of the [info object](http://swagger.io/specification/#infoObject). |
| `description` | A short description of the application. Maps to the `description` field of the [info object](http://swagger.io/specification/#infoObject). |
| `host` | The host serving the API. Maps to the `host` field of the [schema object](http://swagger.io/specification/#schemaObject). |
| `license` | The license information for the API. Maps to the `license` field of the [info object](http://swagger.io/specification/#infoObject). |
| `produces` | A list of MIME types the API can produce. Maps to the `produces` field of the [schema object](http://swagger.io/specification/#schemaObject). |
| `schemes` | The transfer protocol of the API. Maps the the `schemes` field of the [schema object](http://swagger.io/specification/#schemaObject). |
| `terms` | The terms of service for the API. Maps to the `termsOfService` field of the [info object](http://swagger.io/specification/#infoObject). |
| `title` | The title of the application (defaults to the flask app module name). Maps to the `title` field of the [info object](http://swagger.io/specification/#infoObject). |

## Documenting API endpoints

Decorate your API endpoints with `@swagger.doc`. It takes a dictionary in the format of a [swagger operation object](http://swagger.io/specification/#operationObject).

```python
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
        # Do some processing
        return UserModel(id=1, name='somebody'}), 200  # generates json response {"id": 1, "name": "somebody"}

```

Use add_resource as usual.

```python
api.add_resource(UserItemResource, '/api/users/<int:user_id')
```

## Parsing query parameters

If a resource function contains the special argument `_parser`, any `query` type parameters in the
documentation will be automatically added to a reqparse parser and assigned to the `_parser` argument.

## Using models

Create a model by inheriting from `flask.ext.restful_swagger_2.Schema`

```python
from flask.ext.restful_swagger_2 import Schema


class EmailModel(Schema):
    type = 'string'
    format = 'email'


class KeysModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string'
        }
    }


class UserModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': EmailModel,
        'keys': KeysModel.array()
    }
    required = ['name']
```

You can build your models according to the [swagger schema object specification](http://swagger.io/specification/#schemaObject)

It is recommended that you always return a model in your views. This way, you will always keep your code and your documentation in sync.

## Specification document

The `get_swagger_doc` method of the Api instance returns the specification document object,
which may be useful for integration with other tools for generating formatted output or client code.

## Using authentication

In the example above, the view `UserItemResource` is a subclass of `Resource`, which is provided by `flask_restful`. However,
`flask_restful_swagger_2` provides a thin wrapper around `Resource` to provide authentication. By using this, you can
not only prevent access to resources, but also hide the documentation depending on the provided `api_key`.

Example:

```python
# Import Resource instead from flask_restful_swagger_2
from flask.ext.restful_swagger_2 import Api, swagger, Resource

api = Api(app)
def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    # api_key is extracted from the url parameters (?api_key=foo)
    # endpoint is the full swagger url (e.g. /some/{value}/endpoint)
    # method is the HTTP method
    return True

swagger.auth = auth

class MyView(Resource):
    @swagger.doc({
    # documentation...
    })
    def get(self):
        return SomeModel(value=5)

api.add_resource(MyView, '/some/endpoint')
```

## Running and testing

To run the example project in the `example` folder:

```
pip install flask-restful-swagger-2
pip install flask-cors    # needed to access spec from swagger-ui
python app.py
```

The swagger spec will by default be at `http://localhost:5000/api/swagger.json`. You can change the url by passing
`api_spec_url='/my/path'` to the `Api` constructor. You can use [swagger-ui](https://github.com/swagger-api/swagger-ui)
to explore your api. Try it online at [http://petstore.swagger.io/](http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json)

To run tests:

```
python setup.py test
```
