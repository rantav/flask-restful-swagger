import sys

import pytest
from flask_restful import fields

from flask_restful_swagger import swagger


@pytest.mark.parametrize(
    "case_name, test_input, expected",
    [
        ("Null", None, {"type": "null"}),
        ("Simple False", False, {"type": "boolean"}),
        ("Simple True", True, {"type": "boolean"}),
        ("Integer", 1, {"type": "integer"}),
        ("Very large integer", sys.maxsize, {"type": "integer"}),
        ("Float less than 1", 0.8092, {"type": "number"}),
        ("Float greater than 1", 98763.09, {"type": "number"}),
        ("String", "helloWorld!", {"type": "string"}),
    ],
)
def test_deduce_swagger_type_instances(case_name, test_input, expected):
    assert swagger.deduce_swagger_type(test_input) == expected


@pytest.mark.parametrize(
    "field_type, expected",
    [
        ("Boolean", {"type": "boolean"}),
        ("Integer", {"type": "integer"}),
        ("Arbitrary", {"type": "number"}),
        ("Fixed", {"type": "number"}),
        ("DateTime", {"type": "date-time"}),
    ],
)
def test_deduce_swagger_type_flask_field(field_type, expected):
    new_field = getattr(fields, field_type)()
    assert swagger.deduce_swagger_type(new_field) == expected


@pytest.mark.parametrize(
    "case_name, object_type, expected",
    [
        ("Class derived from string", str, {"type": "string"}),
        ("Class derived from integer", int, {"type": "integer"}),
        ("Class derived from float", float, {"type": "number"}),
    ],
)
def test_deduce_swagger_type_create_new_class(
        case_name, object_type, expected):
    class NewSubClass(object_type):
        pass

    new_instance = NewSubClass()
    assert swagger.deduce_swagger_type(new_instance) == expected


@pytest.mark.parametrize(
    "case_name, object_type, expected",
    [
        ("Class derived from string", str, {"type": "string"}),
        ("Class derived from integer", int, {"type": "integer"}),
        ("Class derived from float", float, {"type": "number"}),
        ("Class derived from fields.List", fields.List, {"type": "array"}),
    ],
)
def test_deduce_swagger_type_with_class(case_name, object_type, expected):
    class NewSubClass(object_type):
        pass

    assert swagger.deduce_swagger_type(NewSubClass) == expected


def test_deduce_swagger_type_fields_formatted_string():
    new_instance = fields.FormattedString("Hello {name}")

    assert swagger.deduce_swagger_type(new_instance) == {"type": "string"}


def test_deduce_swagger_type_fields_list_instance():
    new_instance = fields.List(fields.String)

    assert "items" in swagger.deduce_swagger_type(new_instance)


def test_deduce_swagger_type_fields_nested_instance():
    new_instance = fields.Nested({})

    assert swagger.deduce_swagger_type(new_instance) == {"type": None}
