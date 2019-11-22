import os

import pytest

import flask_restful_swagger
from flask_restful_swagger.swagger import StaticFiles

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


test_fixtures_renders = [
    ["index.html", None, None],
    ["o2c.html", None, None],
    ["swagger-ui.js", None, None],
    ["swagger-ui.min.js", None, None],
    ["lib/swagger-oauth.js", None, None],
]


@patch("flask_restful_swagger.swagger.render_page")
@patch("flask_restful_swagger.swagger._get_current_registry")
@pytest.mark.parametrize("dir1,dir2,dir3", test_fixtures_renders)
def test_get_valid_content_renders(registry, render_page, dir1, dir2, dir3):

    static_files = StaticFiles()
    registry.return_value = {"spec_endpoint_path": "dummy"}

    static_files.get(dir1, dir2, dir3)
    assert render_page.call_args[0] == (dir1, {"resource_list_url": "dummy"})


test_fixtures_none = [[None, None, None]]


@patch("flask_restful_swagger.swagger.render_page")
@patch("flask_restful_swagger.swagger._get_current_registry")
@pytest.mark.parametrize("dir1,dir2,dir3", test_fixtures_none)
def test_get_valid_content_renders_none(
    registry, render_page, dir1, dir2, dir3
):

    static_files = StaticFiles()
    registry.return_value = {"spec_endpoint_path": "dummy"}

    static_files.get(dir1, dir2, dir3)
    assert render_page.call_args[0] == (
        "index.html",
        {"resource_list_url": "dummy"},
    )


test_fixtures_mimes = [
    ["index2.html", "text/plain"],
    ["image.gif", "image/gif"],
    ["image.png", "image/png"],
    ["javascript.js", "text/javascript"],
    ["style.css", "text/css"],
]


@patch("flask_restful_swagger.swagger.Response", autospec=True)
@patch("flask_restful_swagger.swagger.open")
@patch("flask_restful_swagger.swagger.os.path.exists")
@patch("flask_restful_swagger.swagger._get_current_registry")
@pytest.mark.parametrize("dir1,mime", test_fixtures_mimes)
def test_get_valid_content_mime(
    registry, mock_exists, mock_open, response, dir1, mime
):

    mock_open.return_value = "file_handle"
    mock_exists.return_value = True

    static_files = StaticFiles()
    static_files.get(dir1, None, None)
    assert mock_exists.called
    assert mock_open.called

    args, kwargs = response.call_args_list[0]
    assert args == ("file_handle",)
    assert kwargs == {"mimetype": mime}


test_fixtures_mimes_does_not_exist = ["index2.html"]


@patch("flask_restful_swagger.swagger.os.path.exists")
@patch("flask_restful_swagger.swagger._get_current_registry")
@patch("flask_restful_swagger.swagger.abort")
@pytest.mark.parametrize("dir1", test_fixtures_mimes_does_not_exist)
def test_get_valid_content_mime_file_does_not_exist(
    abort, registry, mock_exists, dir1
):

    mock_exists.return_value = False
    static_files = StaticFiles()
    static_files.get(dir1, None, None)
    assert mock_exists.called
    assert abort.called


test_fixtures_paths = [
    ["paths", "index2.html", None, "paths/index2.html"],
    ["paths", "more_paths", "index2.html", "paths/more_paths/index2.html"],
]


@patch("flask_restful_swagger.swagger.Response", autospec=True)
@patch("flask_restful_swagger.swagger.os.path.exists")
@patch("flask_restful_swagger.swagger.open")
@patch("flask_restful_swagger.swagger.render_page")
@patch("flask_restful_swagger.swagger._get_current_registry")
@pytest.mark.parametrize("dir1,dir2,dir3,expected", test_fixtures_paths)
def test_get_valid_content_paths(
    registry,
    render_page,
    mock_open,
    mock_exists,
    response,
    dir1,
    dir2,
    dir3,
    expected,
):

    mock_open.return_value = "file_handle"
    mock_exists.return_value = True

    static_files = StaticFiles()
    registry.return_value = {"spec_endpoint_path": "dummy"}

    static_files.get(dir1, dir2, dir3)
    module_path = os.path.dirname(flask_restful_swagger.__file__)
    static_files = "static"
    full_path = os.path.join(module_path, static_files, expected)

    assert mock_exists.called
    assert mock_open.call_args_list[0][0][0] == full_path

    args, kwargs = response.call_args_list[0]
    assert args == ("file_handle",)
    assert kwargs == {"mimetype": "text/plain"}
