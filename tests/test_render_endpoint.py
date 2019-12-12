import unittest

from flask_restful_swagger import swagger

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class Endpoint:
    pass


class TestRenderEndpoint(unittest.TestCase):
    def test_render_endpoint(self):
        endpoint = Endpoint()
        with patch(
            "flask_restful_swagger.swagger.render_page"
        ) as mock_render_page:
            swagger.render_endpoint(endpoint)
            mock_render_page.assert_called_with(
                "endpoint.html", endpoint.__dict__
            )
