from bs4 import BeautifulSoup
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

    assert sorted(bases) == [
        "MethodView",
        "Resource",
        "SwaggerResource",
        "View",
        "object",
    ]

    with app.test_request_context(path="/some_path.help.json"):
        resource_instance = resource()
        response = resource_instance.get()
        assert sorted(list(response.keys())) == [
            "description",
            "notes",
            "operations",
            "path",
        ]
        assert response["path"] == "/some_path"
        assert response["operations"] == []

    with app.test_request_context(path="/some_path.help.html"):
        resource_instance = resource()
        response = resource_instance.get()
        assert response.status_code == 200
        assert isinstance(response.data, bytes)
        assert BeautifulSoup(
            response.data.decode("utf-8"), "html.parser"
        ).find()

    with app.test_request_context(path="/some_path"):
        resource_instance = resource()
        assert resource_instance.get() is None
