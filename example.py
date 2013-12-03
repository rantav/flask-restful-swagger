from flask import Flask, redirect
from flask.ext.restful import reqparse, abort, Api, Resource
from flask_restful_swagger import swagger

app = Flask(__name__)

###################################
# This is important:
api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"])
###################################

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
  if todo_id not in TODOS:
    abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


@swagger.model
class ModelClass:
  pass


@swagger.model
class TodoItem:
  def __init__(self, arg1, arg2, arg3='123'):
    pass


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
  "My TODO API"
  @swagger.operation(
      notes='get a todo item by ID',
      responseClass=ModelClass.__name__,
      nickname='get',
      # Parameters can be automatically extracted from URLs (e.g. <string:id>)
      # but you could also override them here.
      # Overriding the parameters array will override the entire auto extracted
      # parameters.
      parameters=[
          {
            "name": "todo_id_x",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          }
      ])
  def get(self, todo_id):
    # This goes into the summary
    "Get a todo task"
    abort_if_todo_doesnt_exist(todo_id)
    return TODOS[todo_id]

  def delete(self, todo_id):
    abort_if_todo_doesnt_exist(todo_id)
    del TODOS[todo_id]
    return '', 204

  def put(self, todo_id):
    args = parser.parse_args()
    task = {'task': args['task']}
    TODOS[todo_id] = task
    return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
  def get(self):
    return TODOS

  @swagger.operation(
      notes='Creates a new TODO item',
      responseClass=TodoItem.__name__,
      nickname='create',
      parameters=[
          {
            "name": "body",
            "description": "A TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": TodoItem.__name__,
            "paramType": "body"
          }
      ],
      responseMessages=[
          {
              "code": 201,
              "message": "Created. The URL of the created blueprint should " +
              "be in the Location header"
          },
          {
              "code": 405,
              "message": "Invalid input"
          }
      ])
  def post(self):
    args = parser.parse_args()
    todo_id = 'todo%d' % (len(TODOS) + 1)
    TODOS[todo_id] = {'task': args['task']}
    return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')


@app.route('/docs')
def docs():
  return redirect('/static/docs.html')


if __name__ == '__main__':
  ModelClass()
  TodoItem(1, 2, '3')
  app.run(debug=True)
