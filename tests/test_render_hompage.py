from flask_restful_swagger import swagger

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("flask_restful_swagger.swagger.render_page")
@patch("flask.wrappers.Response")
def test_render_hompage_func(response_obj, mock_render_page):
    resource_list_url = "resource_list_url"
    swagger.render_homepage(resource_list_url)
    mock_render_page.assert_called_once_with(
        "index.html", {"resource_list_url": resource_list_url}
    )
