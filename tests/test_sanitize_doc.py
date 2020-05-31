import pytest

from flask_restful_swagger import swagger


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Hey\n", "Hey<br/>"),
        ("\n/n\n/n\n", "<br/>/n<br/>/n<br/>"),
        ("No Change", "No Change"),
    ],
)
def test_string_sanitize_doc(test_input, expected):
    assert swagger._sanitize_doc(test_input) == expected


def test_none_sanitize_doc():
    assert swagger._sanitize_doc(None) is None
