# flask-restful-swagger

flask-restful-swagger is a wrapper for [flask-restful](http://flask-restful.readthedocs.org/en/latest/) which enables [swagger](https://developers.helloreverb.com/swagger/) support.

In essense, you just need to wrap the Api instance and add a few python decorators to get full swagger support.

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
-- TODO

```

Now run your flask app
```
python example.py
```

And visit:
```
curl http://localhost:5000/resources.json
```
