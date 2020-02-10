from flask import Flask

from flask_restful_swagger.swagger import SwaggerRegistry

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("flask_restful_swagger.swagger._get_current_registry")
@patch("flask_restful_swagger.swagger.render_homepage")
def test_get_swagger_registry(homepage, registry):

    mock_registry = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    registry.return_value = mock_registry

    app = Flask(__name__)

    resource = SwaggerRegistry()
    bases = [base.__name__ for base in SwaggerRegistry.__mro__]

    assert sorted(bases) == [
        "MethodView",
        "Resource",
        "SwaggerRegistry",
        "View",
        "object",
    ]

    with app.test_request_context(path="/some_path.html"):
        _ = resource.get()
        assert homepage.called
        homepage.assert_called_once_with(
            "mock_pathmock_spec_endpoint_path/_/resource_list.json"
        )

    with app.test_request_context(path="/some_path"):
        homepage.reset_mock()
        response = resource.get()
        assert not homepage.called
        assert response == mock_registry
