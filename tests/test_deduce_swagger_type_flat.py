import pytest
import datetime

from flask_restful_swagger import swagger
from flask_restful import fields

"""

the "predicate" in the function determines whether
the argument is a class or an instance chooses whether to apply
"issubclass" or "isinstance" to the remaining conditions


Cases

Argument 1:
    String
    integer
    float
    boolean
    date-time
    child class of each of those

Argumentßß 2:
    blank
    None
    Something

"""

# Instances of types
@pytest.mark.parametrize(
    "case_name, test_input, expected",
    [
        ("Null", None, None),
        ("Simple False", False, "boolean"),
        ("Simple True", True, "boolean"),
        ("Integer", 1, "integer"),
        ("Very large integer", 9223372036854775807, "integer"),
        ("Float less than 1", 0.8092, "number"),
        ("Float greater than 1", 98763.09, "number"),
        ("String", "helloWorld!", "string")
    ],
)

def test_deduce_swagger_type_flat_instances(case_name, test_input, expected):
    assert swagger.deduce_swagger_type_flat(test_input) == expected

#instances of fields from flask

@pytest.mark.parametrize(
    "field_type, expected",
    [
        ("Boolean", "boolean"),
        ("Integer", "integer"),
        ("Arbitrary", "number"),
        ("Fixed", "number"),
        ("DateTime", "date-time"),
    ],
)

def test_deduce_swagger_type_flat_flask_field(field_type, expected):
    new_field = getattr(fields, field_type)()
    assert swagger.deduce_swagger_type_flat(new_field) == expected

# Objects that are subclasses
@pytest.mark.parametrize(
    "case_name, object_type, expected",
    [
        ("Class derived from string", str, "string"),
        ("Class derived from integer", int, "integer"),
        ("Class derived from float", float, "number"),
    ],
)

def test_deduce_swagger_type_flat_create_new_class(case_name, object_type, expected):
    class NewSubClass(object_type):
        pass

    new_instance = NewSubClass()
    assert swagger.deduce_swagger_type_flat(new_instance) == expected


def test_deduce_swagger_type_flat_with_nested_object():
    #new_object = fields.Nested({})
    assert swagger.deduce_swagger_type_flat("anything", "cookies") == "cookies"

def test_deduce_swagger_type_flat_with_class():
    class NewSubClass(str):
        pass

    assert swagger.deduce_swagger_type_flat(NewSubClass) == "string"