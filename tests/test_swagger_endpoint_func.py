from flask import Flask
from flask_restful import Resource

from flask_restful_swagger.swagger import swagger_endpoint

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("flask_restful_swagger.swagger._get_current_registry")
def test_get_swagger_endpoint(registry):
    registry.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    class MockResource(Resource):
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    app = Flask(__name__)

    resource = swagger_endpoint("some_api", MockResource, "/some_path")
    bases = [base.__name__ for base in resource.__mro__]
    assert bases == [
        "SwaggerResource",
        "Resource",
        "MethodView",
        "View",
        "object",
    ]

    with app.test_request_context(path="/some_path.help.json"):
        response = resource.get(resource)
        assert list(response.keys()) == [
            "path",
            "description",
            "notes",
            "operations",
        ]

    with app.test_request_context(path="/some_path.help.html"):
        response = resource.get(resource)
        assert response.status_code == 200
        assert isinstance(response.data, bytes)
        assert "Valid HTML?" == "How to check?"

    with app.test_request_context(path="/some_path"):
        assert resource.get(resource) is None
