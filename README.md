# flask-restful-swagger

flask-restful-swagger is a wrapper for [flask-restful](http://flask-restful.readthedocs.org/en/latest/) which enables [swagger](https://developers.helloreverb.com/swagger/) support.

In essense, you just need to wrap the Api instance and add a few python decorators to get full swagger support.

Install: 

```
pip install flask-restful-swagger
```
(This installs flask-restful as well)


And in your program, where you'd usually just use flask-restful, add just a little bit of sauce and get a swagger spec out.


```
from flask import Flask
from flask.ext.restful import  Api
from flask_restful_swagger import swagger

app = Flask(__name__)

###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
api = swagger.docs(Api(app), version='0.1')
###################################


# You may decorate your operation with @swagger.operation
class Todo(Resource):
    "Describing elephants"
    @swagger.operation(
        notes='some really good notes',
        responseClass=ModelClass.__name__,
        nickname='upload',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": ModelClass2.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, todo_id):

# Then you add_resource as you usually would

api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')

# You define models like this:
@swagger.model
class TodoItem:
  "A description ..."
  pass

# Swagger json: 
    "models": {
        "TodoItemWithArgs": {
            "description": "A description...",
            "id": "TodoItem",
        },

# If you declare an __init__ method with meaningful arguments then those args could be used to deduce the swagger model fields. 
@swagger.model
class TodoItemWithArgs:
  "A description ..."
  def __init__(self, arg1, arg2, arg3='123'):
    pass

# Swagger json: 
    "models": {
        "TodoItemWithArgs": {
            "description": "A description...",
            "id": "TodoItem",
            "properties": {
                "arg1": {
                    "type": "string"
                },
                "arg2": {
                    "type": "string"
                },
                "arg3": {
                    "default": "123",
                    "type": "string"
                }
            },
            "required": [
                "arg1",
                "arg2"
            ]
        },


# Additionally, if the model class has a `resource_fields` class member then flask-restful-swagger is able to deduce the swagger spec by this list of fields. 

@swagger.model
class TodoItemWithResourceFields:
  resource_fields = {
      'a_string': fields.String
  }

# Swagger json: 
    "models": {
        "TodoItemWithResourceFields": {
            "id": "TodoItemWithResourceFields",
            "properties": {
                "a_string": {
                    "type": "string"
                },
            }
        }

# And in order to close the loop with flask-restify you'd also need to tell flask-restify to @marshal_with the same list of fields when defining your methods. 
# Example:

@marshal_with(TodoItemWithResourceFields.resource_fields)
def get()
  return ...

```

# Using @marshal_with
Let us recap usage of @marshal_with.  
flask-restful has a decorator `@marshal_with`. With the following setup it's possible to define the swagger model types with the same logic as `@marshal_with`.

You have to:

```
# Define youe model with resource_fields
@swagger.model
class TodoItemWithResourceFields:
  resource_fields = {
      'a_string': fields.String
  }

# And use @marshal_with(YourClass.resource_fields):
@marshal_with(TodoItemWithResourceFields.resource_fields)
def get()
  return ...
```


# Running and testing

Now run your flask app  

```
python example.py
```

And visit:

```
curl http://localhost:5000/api/spec.json
```

# Passing more metadata to swagger
When creating the `swagger.docs` object you may pass additional arguments, such as the following:

```
api_spec_url - where to server the swagger spec from. Default is /api/spec.json

apiVersion - passed directly to swagger as the apiVersion attribute. Default: 0.0

basePath - passed directly to swagger as the basePath attribute. Default: 'http://localhost:5000' (do not include a slash at the end)

resourcePath - same as before. default: '/'

produces - same as before, passed directly to swagger. The default is ["application/json"]

swaggerVersion - passed directly to swagger. Default: 1.2
```

__This project is part of the [Cloudify Cosmo project](https://github.com/CloudifySource/)__