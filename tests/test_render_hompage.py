from unittest.mock import patch

from flask import Response

from flask_restful_swagger import swagger

@patch('flask_restful_swagger.swagger.render_page')
@patch('flask.wrappers.Response')
def test_render_hompage_func(response_obj, mock_render_page):
    resource_list_url = "resource_list_url"
    mock_render_page.return_value = Response()
    swagger.render_homepage(resource_list_url)
    mock_render_page.assert_called_once_with("index.html", {"resource_list_url": resource_list_url})



# def render_homepage(resource_list_url):
#     conf = {"resource_list_url": resource_list_url}
# #     return render_page("index.html", conf)