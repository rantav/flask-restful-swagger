try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

from flask_restful_swagger import swagger
from tests.fixtures_add_model import (
    fixtures_add_model_get_docs, fixtures_add_model_init,
    fixtures_add_model_init_parsing_args,
    fixtures_add_model_with_resource_fields_nested_swagger_metadata,
    fixtures_add_model_with_resource_fields_with_nested,
    fixtures_add_model_with_resource_fields_without_swagger_metadata,
    fixtures_integration_test_add_model, patch_deduce_swagger_type, patch_dir,
    patch_getargspec, patch_hasattr, patch_isinstance, patch_parse_doc,
    patch_registry)


@pytest.mark.parametrize(
    "test_input,properties,required,defaults",
    fixtures_integration_test_add_model,
)
def test_integration_test_add_model(test_input, properties, required, defaults):
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
    with patch_registry() as registry:
        swagger.add_model(test_input)

        assert test_input.__name__ in registry["models"]
        assert "description" in registry["models"][test_input.__name__]
        assert "notes" in registry["models"][test_input.__name__]

        if "resource_fields" in dir(test_input):
            if hasattr(test_input, "required"):
                assert "required" in registry["models"][test_input.__name__]
        else:
            assert "required" in registry["models"][test_input.__name__]

        assert "properties" in registry["models"][test_input.__name__]


@pytest.mark.parametrize("input_model", fixtures_add_model_get_docs)
def test_add_model_get_docs(input_model):
    """Ensure `_parse_doc(...)` is called without issues"""
    with patch_registry(), patch_parse_doc() as mock_parse_doc:
        swagger.add_model(input_model)
        mock_parse_doc.assert_called_once_with(input_model)


@patch("flask_restful_swagger.swagger._Nested", spec=swagger._Nested)
@pytest.mark.parametrize(
    "mock_model_class",
    fixtures_add_model_with_resource_fields_without_swagger_metadata,
)
def test_add_model_with_resource_fields_without_swagger_metadata(
    mock_nested, mock_model_class,
):
    """Test adding model with resource fields, no init, without swagger metadata.
    """
    with patch_registry(), patch_parse_doc(), patch_isinstance(
        False
    ) as mock_isinstance, patch_hasattr() as mock_hasattr, patch_dir(
        ["resource_fields"]
    ) as mock_dir, patch_deduce_swagger_type() as mock_deduce_swagger_type:

        swagger.add_model(mock_model_class)

        mock_dir.assert_called_with(mock_model_class)
        assert mock_dir.call_count == 2
        mock_hasattr.assert_called_once_with(mock_model_class, "required")
        mock_isinstance.assert_called_with(mock_model_class, mock_nested)
        assert mock_deduce_swagger_type.call_count == len(
            mock_model_class.resource_fields.items()
        )


@pytest.mark.parametrize(
    "model_class", fixtures_add_model_with_resource_fields_with_nested
)
def test_add_model_with_resource_fields_with_nested(model_class,):
    """Test for model with resource fields, nested subclass

    * resource_fields: YES
    * nested subclass: YES
    * __init__: NO
    * swagger_metadata:NO

    """
    with patch_registry(), patch_parse_doc(), patch_isinstance(
        True
    ) as mock_isinstance, patch_hasattr() as mock_hasattr, patch_dir(
        ["resource_fields"]
    ) as mock_dir, patch_deduce_swagger_type() as mock_deduce_swagger_type:
        swagger.add_model(model_class)

        mock_dir.assert_called_with(model_class)
        assert mock_dir.call_count == 2
        mock_hasattr.assert_called_once_with(model_class, "required")
        mock_isinstance.assert_called_with(model_class, swagger._Nested)
        assert mock_deduce_swagger_type.call_count == len(
            model_class.resource_fields.items()
        )


@pytest.mark.parametrize(
    "model_class",
    fixtures_add_model_with_resource_fields_nested_swagger_metadata,
)
def test_add_model_with_resource_fields_nested_swagger_metadata(model_class,):
    """Test for model with resource fields, nested subclass, swagger metadata

    * resource_fields: YES
    * nested subclass: YES
    * __init__: NO
    * swagger_metadata:YES
    """
    with patch_registry(), patch_parse_doc(), patch_isinstance(
        True
    ) as mock_isinstance, patch_hasattr() as mock_hasattr, patch_dir(
        ["resource_fields"]
    ) as mock_dir, patch_deduce_swagger_type() as mock_deduce_swagger_type:
        swagger.add_model(model_class)

        mock_dir.assert_called_with(model_class)
        assert mock_dir.call_count == 2
        mock_hasattr.assert_called_once_with(model_class, "required")
        mock_isinstance.assert_called_with(model_class, swagger._Nested)
        assert mock_deduce_swagger_type.call_count == len(
            model_class.resource_fields.items()
        )


@pytest.mark.parametrize("model_class", fixtures_add_model_init)
def test_add_model_init(model_class):
    """Test for model with only init

    * resource_fields: NO
    * nested subclass: NO
    * __init__: YES
    * swagger_metadata: NO
    """
    with patch_registry(), patch_parse_doc(), patch_dir(
        ["__init__"]
    ), patch_getargspec() as mock_getargspec:
        swagger.add_model(model_class)
        mock_getargspec.assert_called_once_with(model_class.__init__)


@pytest.mark.parametrize(
    "model_class,required,defaults", fixtures_add_model_init_parsing_args
)
def test_add_model_init_parsing_args(model_class, required, defaults):
    """Test to verify args parsed correctly
    """
    with patch_registry() as registry, patch_parse_doc(), patch_dir(
        ["__init__"]
    ):
        swagger.add_model(model_class)

        assert model_class.__name__ in registry["models"]
        assert registry["models"][model_class.__name__]["required"] == required
        for key, default_value in defaults:
            _name = model_class.__name__
            assert key in registry["models"][_name]["properties"]
            assert (
                default_value
                == registry["models"][_name]["properties"][key]["default"]
            )
