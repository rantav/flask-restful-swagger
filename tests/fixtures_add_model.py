try:
    from unittest.mock import patch
    from unittest.mock import Mock
except ImportError:
    from mock import patch
    from mock import Mock
from contextlib import contextmanager

from flask_restful import fields

from flask_restful_swagger import swagger


@contextmanager
def patch_registry():
    with patch("flask_restful_swagger.swagger.registry") as mock_registry:
        _temp_dict = {"models": {}}
        mock_registry.__getitem__.side_effect = _temp_dict.__getitem__
        mock_registry.__setitem__.side_effect = _temp_dict.__setitem__
        yield _temp_dict


@contextmanager
def patch_parse_doc():
    with patch("flask_restful_swagger.swagger._parse_doc") as mock_parse_doc:
        mock_parse_doc.return_value = (None, None)
        yield mock_parse_doc


@contextmanager
def patch_deduce_swagger_type():
    with patch(
        "flask_restful_swagger.swagger.deduce_swagger_type"
    ) as mock_deduce_swagger_type:
        mock_deduce_swagger_type.return_value = "dummy_swagger_type"
        yield mock_deduce_swagger_type


@contextmanager
def patch_isinstance(patchbool):
    with patch("flask_restful_swagger.swagger.isinstance") as mock_isinstance:
        mock_isinstance.return_value = patchbool
        yield mock_isinstance


@contextmanager
def patch_hasattr():
    with patch("flask_restful_swagger.swagger.hasattr") as mock_hasattr:
        mock_hasattr.return_value = True
        yield mock_hasattr


@contextmanager
def patch_dir(patchreturn):
    with patch("flask_restful_swagger.swagger.dir") as mock_dir:
        mock_dir.return_value = patchreturn
        yield mock_dir


@contextmanager
def patch_getargspec():
    with patch(
        "flask_restful_swagger.swagger.inspect.getargspec"
    ) as mock_getargspec:
        mock_argspec = Mock()
        mock_argspec.args = ["self", "arg1", "arg2", "arg3"]
        mock_argspec.defaults = ("123",)
        mock_getargspec.return_value = mock_argspec
        yield mock_getargspec


###############################################################################
# Copy setup objects from examples/basic.py
###############################################################################

MockBasicObjectNoInit = Mock()
MockBasicObjectNoInit.__name__ = MockBasicObjectNoInit


class MockBasicObject:
    def __init__(self, arg1):
        pass


class MockBasicWithSwaggerMetadata1:
    def __init__(self, arg1):
        pass

    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


class MockBasicWithSwaggerMetadata2:
    def __init__(self, arg1, an_enum):
        pass

    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


class MockTodoItem:
    """This is an example of a model class that has parameters in its constructor
    and the fields in the swagger spec are derived from the parameters
    to __init__.
    In this case we would have args, arg2 as required parameters and arg3 as
    optional parameter.
    """

    def __init__(self, arg1, arg2, arg3="123"):
        pass


class MockModelWithResourceFieldsNoRequired:
    resource_fields = {"a_string": fields.String()}


class MockModelWithResourceFieldsWithRequired:
    resource_fields = {"a_string": fields.String()}

    required = ["a_string"]


@swagger.nested(
    a_nested_attribute=MockModelWithResourceFieldsNoRequired.__name__,
    a_list_of_nested_types=MockModelWithResourceFieldsNoRequired.__name__,
)
class MockModelWithResourceFieldsWithRequiredWithSwaggerMetadata:
    resource_fields = {
        "a_string": fields.String(),
        "an_enum": fields.String,
    }
    required = ["a_string"]
    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


@swagger.nested(
    a_nested_attribute=MockModelWithResourceFieldsNoRequired.__name__,
    a_list_of_nested_types=MockModelWithResourceFieldsNoRequired.__name__,
)
class MockTodoItemWithResourceFields:
    """This is an example of how Output Fields work
      (http://flask-restful.readthedocs.org/en/latest/fields.html).
      Output Fields lets you add resource_fields to your model in which you
      specify the output of the model when it gets sent as an HTTP response.
      flask-restful-swagger takes advantage of this to specify the fields in
      the model
    """

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
            MockModelWithResourceFieldsNoRequired.resource_fields
        ),
        "a_list_of_nested_types": fields.List(
            fields.Nested(
                MockModelWithResourceFieldsNoRequired.resource_fields
            )
        ),
    }

    # Specify which of the resource fields are required
    required = ["a_string"]


###############################################################################
# Tests Fixtures
###############################################################################

fixtures_integration_test_add_model = [
    (MockBasicObject, [], [], []),
    (MockTodoItem, ["arg1", "arg2", "arg3"], ["arg1", "arg2"], ["arg3"]),
    (MockModelWithResourceFieldsNoRequired, ["a_string"], [], []),
    (
        MockTodoItemWithResourceFields,
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
    (MockBasicWithSwaggerMetadata1, [], [], []),
    (MockBasicWithSwaggerMetadata2, [], [], []),
]

fixtures_add_model_get_docs = [
    MockBasicObject,
    MockTodoItem,
    MockModelWithResourceFieldsNoRequired,
    MockTodoItemWithResourceFields,
]

fixtures_add_model_with_resource_fields_without_swagger_metadata = [
    MockModelWithResourceFieldsWithRequired,
]

fixtures_add_model_with_resource_fields_with_nested = [
    MockTodoItemWithResourceFields,
]

fixtures_add_model_with_resource_fields_nested_swagger_metadata = [
    MockModelWithResourceFieldsWithRequiredWithSwaggerMetadata,
]


fixtures_add_model_no_properties = [
    MockBasicObjectNoInit,
]

fixtures_add_model_init = [
    MockBasicObject,
    MockTodoItem,
]

fixtures_add_model_init_parsing_args = [
    [MockTodoItem, ["arg1", "arg2"], [("arg3", "123")]]
]
