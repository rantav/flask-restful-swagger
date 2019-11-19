import datetime
from unittest.mock import patch

import pytest
from flask import Flask, redirect
from flask_restful import Api, Resource, abort, fields, marshal_with, reqparse

from flask_restful_swagger import registry, swagger


class MockBasicObject:
    pass


class TodoItem:
    """This is an example of a model class that has parameters in its constructor
  and the fields in the swagger spec are derived from the parameters
  to __init__.
  In this case we would have args, arg2 as required parameters and arg3 as
  optional parameter."""

    def __init__(self, arg1, arg2, arg3="123"):
        pass


class ModelWithResourceFields:
    resource_fields = {"a_string": fields.String()}


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


@pytest.mark.parametrize(
    "test_input,properties,required,defaults",
    [
        (MockBasicObject, [], [], []),
        (TodoItem, ["arg1", "arg2", "arg3"], ["arg1", "arg2"], ["arg3"]),
        (ModelWithResourceFields, ["a_string"], [], []),
        (
            TodoItemWithResourceFields,
            [
                "a_string",
                "a_formatted_string",
                "an_enum",
                "an_int",
                "a_bool",
                "a_url",
                "a_float",
                "an_float_with_arbitrary_precision",
                "a_fixed_point_decimal",
                "a_datetime",
                "a_list_of_strings",
                "a_nested_attribute",
                "a_list_of_nested_types",
            ],
            ["a_string"],
            [],
        ),
    ],
)
def test_integration_test_add_model(test_input, properties, required, defaults):
    """Integration test for `add_model(...)` method.
    Ensures models are added to `registry["models"]` with expected structure.
    Example each model should have 'description', 'id','notes',
    'properties', etc.

    Example `registry["models"]`:
        # print(registry["models"])
        {   'models': {   .....
              'TodoItem': {   'description': 'This is an example of a '
                                             'model class that has '
                                             'parameters in its '
                                             'constructor',
                              'id': 'TodoItem',
                              'notes': 'and the fields in the swagger spec '
                                       'are derived from the '
                                       'parameters<br/>to __init__.<br/>In '
                                       'this case we would have args, arg2 '
                                       'as required parameters and arg3 '
                                       'as<br/>optional parameter.',
                              'properties': {   'arg1': {'type': 'string'},
                                                'arg2': {'type': 'string'},
                                                'arg3': {   'default': '123',
                                                            'type': 'string'}},
                              'required': ['arg1', 'arg2']},
                                ..........
    """
    swagger.add_model(test_input)

    assert test_input.__name__ in registry["models"]
    assert "description" in registry["models"][test_input.__name__]
    assert "notes" in registry["models"][test_input.__name__]

    if "resource_fields" in dir(test_input):
        if hasattr(test_input, "required"):
            assert "required" in registry["models"][test_input.__name__]
    else:
        # if "__init__" in dir(test_input):
        assert "required" in registry["models"][test_input.__name__]

    assert "properties" in registry["models"][test_input.__name__]

    print(test_input)
    print(dir(test_input))


# test_add_model(TodoItem)
# test_add_model(MockBasicObject)
# test_add_model(ModelWithResourceFields)
# test_add_model(TodoItemWithResourceFields)
# # print(registry)
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(registry)


