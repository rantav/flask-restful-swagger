from flask_restful_swagger.swagger import _get_current_registry

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_get_current_registry():
    pass
