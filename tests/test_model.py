import datetime

import pytest

from flask_restful_swagger import swagger

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestEmptyClass:
    pass


@pytest.mark.parametrize(
    "test_input",
    [
        TestEmptyClass,  # Test a class
        "im a str",  # Test a str
        123,  # Test int
        None,  # Test None
        datetime.datetime.now(),  # Test datetime
    ],
)
def test_model_with_input(test_input):
    with patch("flask_restful_swagger.swagger.add_model") as mock_add_model:
        assert swagger.model(test_input) == test_input
        mock_add_model.assert_called_once_with(test_input)
