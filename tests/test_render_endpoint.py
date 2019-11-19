import unittest
from unittest.mock import patch

from flask_restful_swagger import swagger


class Endpoint:
    pass


class RenderEndpointTestCast(unittest.TestCase):
    def test_render_endpoint(self):
        endpoint = Endpoint()
        with patch(
            "flask_restful_swagger.swagger.render_page"
        ) as mock_render_page:
            swagger.render_endpoint(endpoint)
            mock_render_page.assert_called_with(
                "endpoint.html", endpoint.__dict__
            )
