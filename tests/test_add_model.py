try:
    from unittest.mock import patch
    from unittest.mock import Mock
except ImportError:
    from mock import patch
    from mock import Mock

import pytest

from flask_restful_swagger import swagger
from tests.fixtures_add_model import (
    fixtures_add_model_get_docs, fixtures_add_model_init,
    fixtures_add_model_init_parsing_args,
    fixtures_add_model_with_resource_fields_nested_swagger_metadata,
    fixtures_add_model_with_resource_fields_with_nested,
    fixtures_add_model_with_resource_fields_without_swagger_metadata,
    fixtures_integration_test_add_model)


@patch("flask_restful_swagger.swagger.registry")
@pytest.mark.parametrize(
    "test_input,properties,required,defaults",
    fixtures_integration_test_add_model,
)
def test_integration_test_add_model(
    mock_registry, test_input, properties, required, defaults
):
    """Integration test for `add_model(...)` method.

    Ensures models are added to `registry["models"]` with expected structure.
    Example each model should have 'description', 'id','notes', 'properties',
    etc.
    Example `registry["models"]`:
        # print(registry["models"])
        {   'models': {   .....
              'MockTodoItem': {   'description': 'This is an example of a '
                                             'model class that has '
                                             'parameters in its '
                                             'constructor',
                              'id': 'MockTodoItem',
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


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("input_model", fixtures_add_model_get_docs)
def test_add_model_get_docs(mock_parse_doc, mock_registry, input_model):
    """Ensure `_parse_doc(...)` is called without issues"""
    _mock_registry = {"models": {}}
    mock_registry.__getitem__.side_effect = _mock_registry.__getitem__
    mock_registry.__setitem__.side_effect = _mock_registry.__setitem__
    mock_parse_doc.return_value = (None, None)
    swagger.add_model(input_model)

    mock_parse_doc.assert_called_once_with(input_model)


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger._Nested", spec=swagger._Nested)
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize(
    "mock_model_class",
    fixtures_add_model_with_resource_fields_without_swagger_metadata,
)
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
    """Test adding model with resource fields, no init, without swagger metadata.
    """
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


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize(
    "model_class", fixtures_add_model_with_resource_fields_with_nested
)
def test_add_model_with_resource_fields_with_nested(
    mock_parse_doc,
    mock_dir,
    mock_hasattr,
    mock_isinstance,
    mock_deduce_swagger_type,
    mock_registry,
    model_class,
):
    """Test for model with resource fields, nested subclass

    * resource_fields: YES
    * nested subclass: YES
    * __init__: NO
    * swagger_metadata:NO

    """
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


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.deduce_swagger_type")
@patch("flask_restful_swagger.swagger.isinstance")
@patch("flask_restful_swagger.swagger.hasattr")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize(
    "model_class",
    fixtures_add_model_with_resource_fields_nested_swagger_metadata,
)
def test_add_model_with_resource_fields_nested_swagger_metadata(
    mock_parse_doc,
    mock_dir,
    mock_hasattr,
    mock_isinstance,
    mock_deduce_swagger_type,
    mock_registry,
    model_class,
):
    """Test for model with resource fields, nested subclass, swagger metadata

    * resource_fields: YES
    * nested subclass: YES
    * __init__: NO
    * swagger_metadata:YES
    """
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


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.inspect.getargspec")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize("model_class", fixtures_add_model_init)
def test_add_model_init(
    mock_parse_doc, mock_dir, mock_getargspec, mock_registry, model_class
):
    """Test for model with only init

    * resource_fields: NO
    * nested subclass: NO
    * __init__: YES
    * swagger_metadata: NO
    """
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


@patch("flask_restful_swagger.swagger.registry")
@patch("flask_restful_swagger.swagger.dir")
@patch("flask_restful_swagger.swagger._parse_doc")
@pytest.mark.parametrize(
    "model_class,required,defaults", fixtures_add_model_init_parsing_args
)
def test_add_model_init_parsing_args(
    mock_parse_doc, mock_dir, mock_registry, model_class, required, defaults
):
    """Test to verify args parsed correctly
    """
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
