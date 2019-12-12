from unittest.mock import MagicMock, Mock, patch

import pytest
from flask_restful import fields

from flask_restful_swagger import swagger

###############################################################################
# Copy setup objects from examples/basic.py
###############################################################################


class MockBasicObject:
    pass


class MockBasicWithSwaggerMetadata1:
    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}

class MockBasicWithSwaggerMetadata2:
    def __init__(self, arg1, an_enum):
        pass

    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


class TodoItem:
    """This is an example of a model class that has parameters in its constructor
    and the fields in the swagger spec are derived from the parameters
    to __init__.
    In this case we would have args, arg2 as required parameters and arg3 as
    optional parameter.
    """

    def __init__(self, arg1, arg2, arg3="123"):
        pass


class ModelWithResourceFieldsNoRequired:
    resource_fields = {"a_string": fields.String()}


class ModelWithResourceFieldsWithRequired:
    resource_fields = {"a_string": fields.String()}

    required = ["a_string"]


@swagger.nested(
    a_nested_attribute=ModelWithResourceFieldsNoRequired.__name__,
    a_list_of_nested_types=ModelWithResourceFieldsNoRequired.__name__,
)
class ModelWithResourceFieldsWithRequiredWithSwaggerMetadata:
    resource_fields = {
        "a_string": fields.String(),
        "an_enum": fields.String,
    }
    required = ["a_string"]
    swagger_metadata = {"an_enum": {"enum": ["one", "two", "three"]}}


@swagger.nested(
    a_nested_attribute=ModelWithResourceFieldsNoRequired.__name__,
    a_list_of_nested_types=ModelWithResourceFieldsNoRequired.__name__,
)
class TodoItemWithResourceFields:
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
            ModelWithResourceFieldsNoRequired.resource_fields
        ),
        "a_list_of_nested_types": fields.List(
            fields.Nested(ModelWithResourceFieldsNoRequired.resource_fields)
        ),
    }

    # Specify which of the resource fields are required
    required = ["a_string"]


###############################################################################
# Pytest code
###############################################################################


# Setup integration test: adds models to the global `registry` and
# test data structure is as expected
test_fixtures = [
    (MockBasicObject, [], [], []),
    (TodoItem, ["arg1", "arg2", "arg3"], ["arg1", "arg2"], ["arg3"]),
    (ModelWithResourceFieldsNoRequired, ["a_string"], [], []),
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
    (MockBasicWithSwaggerMetadata1, [], [], []),
    (MockBasicWithSwaggerMetadata2, [], [], []),
]


@patch("flask_restful_swagger.swagger.registry")
@pytest.mark.parametrize(
    "test_input,properties,required,defaults", test_fixtures
)
def test_integration_test_add_model(
    mock_registry, test_input, properties, required, defaults
):
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
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__

    swagger.add_model(test_input)

    assert test_input.__name__ in _mock_registry["models"]
    assert "description" in _mock_registry["models"][test_input.__name__]
    assert "notes" in _mock_registry["models"][test_input.__name__]

    if "resource_fields" in dir(test_input):
        if hasattr(test_input, "required"):
            assert "required" in _mock_registry["models"][test_input.__name__]
    else:
        assert "required" in _mock_registry["models"][test_input.__name__]

    assert "properties" in _mock_registry["models"][test_input.__name__]


# Setup test - ensure `_parse_doc(..)` is called without issues
test_fixtures_model_inputs = [
    MockBasicObject,
    TodoItem,
    ModelWithResourceFieldsNoRequired,
    TodoItemWithResourceFields,
]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("input_model", test_fixtures_model_inputs)
def test_add_model_get_docs(mock_parse_doc, mock_registry, input_model):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    swagger.add_model(input_model)

    mock_parse_doc.assert_called_once_with(input_model)


# Setup test for - with resource fields, no init, without swagger metadata.
mock_with_resource_fields_with_required = MagicMock(
    spec=ModelWithResourceFieldsWithRequired
)
mock_with_resource_fields_with_required.__name__ = "mock_name_attribute"
mock_with_resource_fields_with_required.resource_fields.items = Mock(
    return_value=dict(a=1, b=2).items()
)


test_fixtures_model_inputs = [
    mock_with_resource_fields_with_required,
]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger._Nested", spec=swagger._Nested)
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("mock_model_class", test_fixtures_model_inputs)
def test_add_model_with_resource_fields_without_swagger_metadata(
    mock_parse_doc,
    mock_dir,
    mock_hasattr,
    mock_isinstance,
    mock_nested,
    mock_deduce_swagger_type,
    mock_registry,
    mock_model_class,
):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    mock_hasattr.return_value = True
    mock_dir.return_value = ["resource_fields"]
    mock_isinstance.return_value = False
    mock_deduce_swagger_type.return_value = "dummy_swagger_type"

    swagger.add_model(mock_model_class)

    mock_dir.assert_called_with(mock_model_class)
    assert mock_dir.call_count == 2
    mock_hasattr.assert_called_once_with(mock_model_class, "required")
    mock_isinstance.assert_called_with(mock_model_class, mock_nested)
    assert mock_deduce_swagger_type.call_count == len(
        mock_model_class.resource_fields.items()
    )


# Setup test for:
#     * resource_fields: YES
#     * nested subclass: YES
#     * __init__: NO
#     * swagger_metadata:NO

test_fixtures_model_inputs = [
    TodoItemWithResourceFields,
]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("model_class", test_fixtures_model_inputs)
def test_add_model_with_resource_fields_with_nested(
    mock_parse_doc,
    mock_dir,
    mock_hasattr,
    mock_isinstance,
    mock_deduce_swagger_type,
    mock_registry,
    model_class,
):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    mock_hasattr.return_value = True
    mock_dir.return_value = ["resource_fields"]
    mock_isinstance.return_value = True
    mock_deduce_swagger_type.return_value = "dummy_swagger_type"

    swagger.add_model(model_class)

    mock_dir.assert_called_with(model_class)
    assert mock_dir.call_count == 2
    mock_hasattr.assert_called_once_with(model_class, "required")
    mock_isinstance.assert_called_with(model_class, swagger._Nested)
    assert mock_deduce_swagger_type.call_count == len(
        model_class.resource_fields.items()
    )


# Setup test for:
#     * resource_fields: YES
#     * nested subclass: YES
#     * __init__: NO
#     * swagger_metadata:YES

test_fixtures_model_inputs = [
    ModelWithResourceFieldsWithRequiredWithSwaggerMetadata,
]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("model_class", test_fixtures_model_inputs)
def test_add_model_with_resource_fields_nested_swagger_metadata(
    mock_parse_doc,
    mock_dir,
    mock_hasattr,
    mock_isinstance,
    mock_deduce_swagger_type,
    mock_registry,
    model_class,
):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    mock_hasattr.return_value = True
    mock_dir.return_value = ["resource_fields"]
    mock_isinstance.return_value = True
    mock_deduce_swagger_type.return_value = "dummy_swagger_type"

    swagger.add_model(model_class)

    mock_dir.assert_called_with(model_class)
    assert mock_dir.call_count == 2
    mock_hasattr.assert_called_once_with(model_class, "required")
    mock_isinstance.assert_called_with(model_class, swagger._Nested)
    assert mock_deduce_swagger_type.call_count == len(
        model_class.resource_fields.items()
    )


# Setup test for:
#     * resource_fields: NO
#     * nested subclass: NO
#     * __init__: YES
#     * swagger_metadata: NO

test_fixtures_model_inputs = [
    MockBasicObject,
    TodoItem,
]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.inspect.getargspec")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("model_class", test_fixtures_model_inputs)
def test_add_model_init(
    mock_parse_doc, mock_dir, mock_getargspec, mock_registry, model_class
):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    mock_dir.return_value = ["__init__"]

    mock_argspec = Mock()
    mock_argspec.args = ["self", "arg1", "arg2", "arg3"]
    mock_argspec.defaults = ("123",)
    mock_getargspec.return_value = mock_argspec

    swagger.add_model(model_class)

    mock_getargspec.assert_called_once_with(model_class.__init__)


# Setup test to verify args parsed correctly
test_fixtures_model_inputs = [[TodoItem, ["arg1", "arg2"], [("arg3", "123")]]]


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize(
    "model_class,required,defaults", test_fixtures_model_inputs
)
def test_add_model_init_parsing_args(
    mock_parse_doc, mock_dir, mock_registry, model_class, required, defaults
):
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    mock_dir.return_value = ["__init__"]

    swagger.add_model(model_class)

    assert model_class.__name__ in _mock_registry["models"]
    assert (
        _mock_registry["models"][model_class.__name__]["required"] == required
    )
    for key, default_value in defaults:
        _name = model_class.__name__
        assert key in _mock_registry["models"][_name]["properties"]
        assert (
            default_value
            == _mock_registry["models"][_name]["properties"][key]["default"]
        )
