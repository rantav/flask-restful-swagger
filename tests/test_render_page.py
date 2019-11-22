from unittest.mock import mock_open, patch

from flask import Response

from flask_restful_swagger import swagger


@patch("flask_restful_swagger.swagger._get_current_registry")
@patch("flask_restful_swagger.swagger.open", new_callable=mock_open)
def test_render_page(mock_open, test_reg):
    test_reg.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    result = swagger.render_page("docs.html", None)
    assert isinstance(result, Response)


@patch("flask_restful_swagger.swagger._get_current_registry")
@patch("flask_restful_swagger.swagger.open", new_callable=mock_open)
def test_render_page_with_slash(mock_open, test_reg):
    test_reg.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path/",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    result_with_trailing_slash = swagger.render_page(
        "docs.html", {"some info": "info"}
    )
    assert isinstance(result_with_trailing_slash, Response)


@patch("flask_restful_swagger.swagger._get_current_registry")
@patch("flask_restful_swagger.swagger.open", new_callable=mock_open)
def test_render_page_in_js(mock_open, test_reg):
    test_reg.return_value = {
        "apiVersion": "mock_version",
        "swaggerVersion": "mock_swagger_version",
        "basePath": "mock_path/",
        "spec_endpoint_path": "mock_spec_endpoint_path",
        "description": "mock_description",
    }

    result_with_js = swagger.render_page("docs.js", {"some info": "info"})
    assert (
        result_with_js.headers["Content-Type"]
        == "text/javascript; charset=utf-8"
    )
