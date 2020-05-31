"""
Running:

  PYTHONPATH=. python examples/basic.py

"""


from flask import Flask, redirect
from flask_restful import Api, Resource, abort, fields, marshal_with, reqparse

from flask_restful_swagger import swagger

app = Flask(__name__, static_folder="../static")

###################################
# This is important:
api = swagger.docs(
    Api(app),
    apiVersion="0.1",
    basePath="http://localhost:5000",
    resourcePath="/",
    produces=["application/json", "text/html"],
    api_spec_url="/api/spec",
    description="A Basic API",
)
###################################

TODOS = {
    "todo1": {"task": "build an API"},
    "todo2": {"task": "?????"},
    "todo3": {"task": "profit!"},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument("task", type=str)


@swagger.model
class TodoItem:
    """This is an example of a model class that has parameters in its constructor
  and the fields in the swagger spec are derived from the parameters
  to __init__.
  In this case we would have args, arg2 as required parameters and arg3 as
  optional parameter."""

    def __init__(self, arg1, arg2, arg3="123"):
        pass


class Todo(Resource):
    "My TODO API"

    @swagger.operation(
        notes="get a todo item by ID",
        nickname="get",
        # Parameters can be automatically extracted from URLs.
        #   For Example: <string:id>
        # but you could also override them here, or add other parameters.
        parameters=[
            {
                "name": "todo_id_x",
                "description": "The ID of the TODO item",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path",
            },
            {
                "name": "a_bool",
                "description": "The ID of the TODO item",
                "required": True,
                "allowMultiple": False,
                "dataType": "boolean",
                "paramType": "path",
            },
        ],
    )
    def get(self, todo_id):
        # This goes into the summary
        """Get a todo task

    This will be added to the <strong>Implementation Notes</strong>.
    It lets you put very long text in your api.

    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
    veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
    velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
    cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
    est laborum.
    """
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id], 200, {"Access-Control-Allow-Origin": "*"}

    @swagger.operation(notes="delete a todo item by ID",)
    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return "", 204, {"Access-Control-Allow-Origin": "*"}

    @swagger.operation(notes="edit a todo item by ID",)
    def put(self, todo_id):
        args = parser.parse_args()
        task = {"task": args["task"]}
        TODOS[todo_id] = task
        return task, 201, {"Access-Control-Allow-Origin": "*"}

    def options(self, **args):
        # since this method is not decorated with @swagger.operation it does
        # not get added to the swagger docs
        return (
            {"Allow": "GET,PUT,POST,DELETE"},
            200,
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS, 200, {"Access-Control-Allow-Origin": "*"}

    @swagger.operation(
        notes="Creates a new TODO item",
        responseClass=TodoItem.__name__,
        nickname="create",
        parameters=[
            {
                "name": "body",
                "description": "A TODO item",
                "required": True,
                "allowMultiple": False,
                "dataType": TodoItem.__name__,
                "paramType": "body",
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created. The URL of the created blueprint should "
                + "be in the Location header",
            },
            {"code": 405, "message": "Invalid input"},
        ],
    )
    def post(self):
        args = parser.parse_args()
        todo_id = "todo%d" % (len(TODOS) + 1)
        TODOS[todo_id] = {"task": args["task"]}
        return TODOS[todo_id], 201, {"Access-Control-Allow-Origin": "*"}


@swagger.model
class ModelWithResourceFields:
    resource_fields = {"a_string": fields.String()}


@swagger.model
@swagger.nested(
    a_nested_attribute=ModelWithResourceFields.__name__,
    a_list_of_nested_types=ModelWithResourceFields.__name__,
)
class TodoItemWithResourceFields:
    """This is an example of how Output Fields work
  (http://flask-restful.readthedocs.org/en/latest/fields.html).
  Output Fields lets you add resource_fields to your model in which you specify
  the output of the model when it gets sent as an HTTP response.
  flask-restful-swagger takes advantage of this to specify the fields in
  the model"""

    resource_fields = {
        "a_string": fields.String(attribute="a_string_field_name"),
        "a_formatted_string": fields.FormattedString,
        "an_enum": fields.String,
        "an_int": fields.Integer,
        "a_bool": fields.Boolean,
        "a_url": fields.Url,
        "a_float": fields.Float,
        "an_float_with_arbitrary_precision": fields.Arbitrary,
        "a_fixed_point_decimal": fields.Fixed,
        "a_datetime": fields.DateTime,
        "a_list_of_strings": fields.List(fields.String),
        "a_nested_attribute": fields.Nested(
            ModelWithResourceFields.resource_fields
        ),
        "a_list_of_nested_types": fields.List(
            fields.Nested(ModelWithResourceFields.resource_fields)
        ),
    }

    # Specify which of the resource fields are required
    required = ["a_string"]

    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


class MarshalWithExample(Resource):
    @swagger.operation(
        notes="get something",
        responseClass=TodoItemWithResourceFields,
        nickname="get",
    )
    @marshal_with(TodoItemWithResourceFields.resource_fields)
    def get(self, **kwargs):
        return {}, 200, {"Access-Control-Allow-Origin": "*"}


#
# Actually setup the Api resource routing here
#
api.add_resource(TodoList, "/todos")
api.add_resource(Todo, "/todos/<string:todo_id>")
api.add_resource(MarshalWithExample, "/marshal_with")


@app.route("/docs")
def docs():
    return redirect("/static/docs.html")


if __name__ == "__main__":
    TodoItemWithResourceFields()
    TodoItem(1, 2, "3")
    app.run(host='0.0.0.0', debug=True)
