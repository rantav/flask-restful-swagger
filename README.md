# flask-restful-swagger-2.0

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
# It takes just two more (optional) parameters, these are the defaults:
api = Api(app, api_version='0.0', api_spec_url='/api/swagger')
```

## Documenting API endpoints
Decorate your API endpoints with `@swagger.doc`. It takes a dictionary in the format of a [swagger operation object](http://swagger.io/specification/#operationObject).

```python
class Todo(Resource):
    @swagger.doc({
        'tags': ['Some', 'Tags'],
        'description': 'My description',
        'summary': 'does things',
        'parameters': [
            {
                'name': 'foo',
                'description': 'awesome stuff',
                'in': 'query',
                'type': 'string',
            }
        ],
        'responses': {
            '200': {
                'description': 'supergeil',
                'schema': MyModel # Take a look at the models sections
            }
        }
    })
    def get(self, todo_id):
        # do some stuff
        return MyModel(foo=5, bar='batz') # generates json response {"foo": 5, "bar": "batz"}
```

Use add_resource as usually.

```python
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')
```

## Using models
Create a model by inheriting from `flask.ext.restful_swagger_2.Schema`

```python
from flask.ext.restful_swagger_2 import Schema


class MyModel(Schema):
    type = 'string'
    format = 'email'


class MyOtherModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': MyModel,
        'moreMails': MyModel.array()
    }
    required = ['name']
```

You can build your models according to the [swagger schema object specification](http://swagger.io/specification/#schemaObject)

It is recommended that you always return a model in your views. This way, you will always keep your code and your
documentation in sync.

# Using authentication

In the example above, the view `Todo` was a subclass of `Resource`. `Resource` is provided by `flask_restful`. However,
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

# Running and testing

Run your flask app as usual

```
python example.py
```

The swagger spec will by default be at `http://localhost:5000/api/swagger.json`. You can change the url by passing
`api_spec_url='/my/path'` to the `Api` constructor. You can use swagger-ui to explore your api. Try it online at
[http://petstore.swagger.io/](http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json)