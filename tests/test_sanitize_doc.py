import pytest
from flask_restful_swagger import swagger

@pytest.mark.parametrize(
    "test_input,expected",
    [("Hey\n", "Hey<br/>"),
     ("\n/n\n/n\n", "<br/>/n<br/>/n<br/>")]
)
def test_string_sanitize_doc(test_input, expected):
    """Uses string cases"""
    assert swagger._sanitize_doc(test_input) == expected


@pytest.mark.parametrize(
    "test_input_types, expected_output",
    [(str(12345) + "\n", "12345<br/>"),
     (str(23+45+31.689923) + "\n", "99.689923<br/>"),
     (str((2 / 1)) + str(2 % 1) + "\/\/\n/\\", "2.00\/\/<br/>/\\")]
)
def test_numbers_sanitize_doc(test_input_types, expected_output):
    assert swagger._sanitize_doc(test_input_types) == expected_output


def test_purenum_sanitize_doc():
    try:
        numbers = 6736+32843.73828932+0.138238
        sentence = "I was able to do this a "
        ending = " times.\nWhat do you think?"
        assert isinstance(swagger._sanitize_doc(sentence + numbers + ending), TypeError)
    except TypeError:
        assert True


def test_zero_errors_sanitize_doc():
    try:
        sentence = "I was able to make $"
        numbers = 99999999999/0
        ending = "\np/m"
        assert isinstance(swagger._sanitize_doc(sentence + numbers + ending), ZeroDivisionError)
    except ZeroDivisionError:
        assert True


def test_none_sanitize_doc():
    try:
        none_var = None
        assert isinstance(swagger._sanitize_doc(none_var), AssertionError)
    except AssertionError:
        assert True


@pytest.mark.parametrize(
    "test_input_types, expected_output",
    [("\r\n\'\/\n/'n", "\r<br/>'\\/<br/>/'n")]
)
def test_escape_characters_sanitize_doc(test_input_types, expected_output):
    assert swagger._sanitize_doc(test_input_types) == expected_output