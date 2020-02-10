import pytest
from flask_restful import Resource

from flask_restful_swagger.swagger import SwaggerEndpoint, operation
from .lib.helpers import TestCaseSupport

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class MockDataType(object):
    pass


tc = TestCaseSupport()
tc.maxDiff = None


@patch("flask_restful_swagger.swagger.extract_swagger_path")
@patch("flask_restful_swagger.swagger.extract_path_arguments")
@patch("flask_restful_swagger.swagger._parse_doc")
@patch("flask_restful_swagger.swagger.SwaggerEndpoint.extract_operations")
def test_swagger_endpoint(operations, docs, args, path):

    path.return_value = "Sometime Soon"
    args.return_value = "I Will Return"
    docs.return_value = ("A Description Will Follow", "As to Where to Meet")
    operations.return_value = ["knee surgery", "back surgery"]

    endpoint = SwaggerEndpoint("Fake Resource", "/some/path")

    assert path.called
    assert args.called
    assert docs.called
    assert operations.called

    assert endpoint.path == "Sometime Soon"
    assert endpoint.description == "A Description Will Follow"
    assert endpoint.notes == "As to Where to Meet"
    assert endpoint.operations == ["knee surgery", "back surgery"]

    operations.assert_called_once_with("Fake Resource", "I Will Return")


def test_swagger_endpoint_extract_operations_empty():
    class MockResource(Resource):
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    assert SwaggerEndpoint.extract_operations(MockResource, []) == []


@pytest.mark.parametrize(
    "mock_properties, update_with",
    [
        (
            {
                "name": "one",
                "method": "get",
                "other": MockDataType,
                "parameters": [
                    {
                        "name": "identifier",
                        "description": "identifier",
                        "required": True,
                        "allowMultiple": False,
                        "dataType": "string",
                        "paramType": "path",
                    },
                    {
                        "name": "identifier2",
                        "description": "identifier2",
                        "required": True,
                        "allowMultiple": False,
                        "dataType": "float",
                        "paramType": "path",
                    },
                ],
            },
            {
                "method": "get<br/>get",
                "nickname": "nickname",
                "summary": None,
                "notes": None,
                "other": "MockDataType",
            },
        ),
    ],
)
@patch("flask_restful_swagger.swagger._get_current_registry")
def test_get_swagger_endpoint_not_subclassed_basic_example(
    registry, mock_properties, update_with
):

    registry.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    class MockResource(Resource):
        @operation(**mock_properties)
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    return_value = SwaggerEndpoint.extract_operations(
        MockResource,
        [
            {"name": "identifier", "dataType": "string", "paramType": "path"},
            {"name": "identifier2", "dataType": "float", "paramType": "path"},
        ],
    )
    mock_properties.update(update_with)
    tc.assertDictEqual(return_value[0], mock_properties)


@pytest.mark.parametrize(
    "mock_properties, update_with",
    [
        (
            {
                "name": "one",
                "method": "get",
                "other": MockDataType,
                "parameters": [
                    {
                        "name": "identifier",
                        "description": "identifier",
                        "required": True,
                        "allowMultiple": False,
                        "dataType": "string",
                        "paramType": "path",
                    },
                    {
                        "name": "identifier2",
                        "description": "identifier2",
                        "required": True,
                        "allowMultiple": False,
                        "dataType": "float",
                        "paramType": "path",
                    },
                ],
            },
            {
                "method": "get<br/>get",
                "nickname": "nickname",
                "summary": None,
                "notes": None,
                "other": "MockDataType",
            },
        ),
    ],
)
@patch("flask_restful_swagger.swagger._get_current_registry")
def test_get_swagger_endpoint_subclassed_basic_example(
    registry, mock_properties, update_with
):

    registry.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    class MockResource(Resource):
        @operation(**mock_properties)
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    class MockSubClass(MockResource):
        pass

    return_value = SwaggerEndpoint.extract_operations(
        MockSubClass,
        [
            {"name": "identifier", "dataType": "string", "paramType": "path"},
            {"name": "identifier2", "dataType": "float", "paramType": "path"},
        ],
    )
    mock_properties.update(update_with)
    tc.assertDictEqual(return_value[0], mock_properties)
