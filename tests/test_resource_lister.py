from flask_restful_swagger.swagger import ResourceLister

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("flask_restful_swagger.swagger.render_page")
@patch("flask_restful_swagger.swagger._get_current_registry")
def test_get_valid_content_renders(registry, render_page):

    expected_result = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "apis": [
            {
                "path": "mock_pathmock_spec_endpoint_path",
                "description": "mock_description",
            }
        ],
    }

    registry.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }
    resource_lister = ResourceLister()
    assert resource_lister.get() == expected_result
