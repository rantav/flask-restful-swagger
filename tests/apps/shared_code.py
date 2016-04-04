# -*- coding: utf-8 -*-

from flask.ext.restful import Resource, fields, marshal_with
from flask_restful_swagger import swagger

__author__ = 'sobolevn'


TODO_ITEM = 'test-item'


@swagger.model
class TodoItem(object):
    def __init__(self, arg1, arg2, arg3='123'):
        pass


@swagger.model
class ModelWithResourceFields:
    resource_fields = {
        'a_string': fields.String(),
    }


@swagger.model
@swagger.nested(
    a_nested_attribute=ModelWithResourceFields.__name__,
    a_list_of_nested_types=ModelWithResourceFields.__name__,
)
class TodoItemWithResourceFields(object):
    """This is an example of how Output Fields work
    (http://flask-restful.readthedocs.org/en/latest/fields.html).
    Output Fields lets you add resource_fields to your model in which you specify
    the output of the model when it gets sent as an HTTP response.
    flask-restful-swagger takes advantage of this to specify the fields in
    the model"""
    resource_fields = {
        'a_string': fields.String(attribute='a_string_field_name'),
        'a_formatted_string': fields.FormattedString,
        'an_int': fields.Integer,
        'a_bool': fields.Boolean,
        'a_url': fields.Url,
        'a_float': fields.Float,
        'an_float_with_arbitrary_precision': fields.Arbitrary,
        'a_fixed_point_decimal': fields.Fixed,
        'a_datetime': fields.DateTime,
        'a_list_of_strings': fields.List(fields.String),
        'a_nested_attribute': fields.Nested(
                ModelWithResourceFields.resource_fields),
        'a_list_of_nested_types': fields.List(
                fields.Nested(ModelWithResourceFields.resource_fields)),
    }

    # Specify which of the resource fields are required
    required = ['a_string', ]


class Todo(Resource):
    """
    Todo-Description
    Todo-Notes
    """

    @swagger.operation(
        notes='get a todo item by ID',
        nickname='get',
        parameters=[{
            'name': 'todo_id_x',
            'description': 'The ID of the TODO item',
            'required': True,
            'allowMultiple': False,
            'dataType': 'string',
            'paramType': 'path',
        },{
            'name': 'a_bool',
            'description': 'The ID of the TODO item',
            'required': True,
            'allowMultiple': False,
            'dataType': 'boolean',
            'paramType': 'path',
        }, ]
    )
    def get(self, todo_id):
        """Summary"""

        # We expect this method to be in our specs.
        return '{}{}'.format(TODO_ITEM, todo_id), 200, {
            'Access-Control-Allow-Origin': '*',
        }

    def options(self, **args):
        # We do not expect this method to be inside json-specs.
        return {
            'Allow': 'GET',
        }, 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        }


class MarshalWithExample(Resource):
    @swagger.operation(
        notes=u'get something',
        responseClass=TodoItemWithResourceFields,
        nickname=u'get',
    )
    @marshal_with(ModelWithResourceFields.resource_fields)
    def get(self, **kwargs):
        return {
            'a_string': 'marshaled',
        }, 200, {
            'Access-Control-Allow-Origin': '*',
        }
