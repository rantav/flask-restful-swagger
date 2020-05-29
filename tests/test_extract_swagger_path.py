import pytest

from flask_restful_swagger import swagger


@pytest.mark.parametrize(
    "case_name, test_input, expected",
    [
        ("empty_string", "", ""),
        ("simple", "/endpoint", "/endpoint"),
        ("single_parameter_no_type", "/path/<parameter>", "/path/{parameter}"),
        (
            "single_parameter_string",
            "/<string(length=2):lang_code>",
            "/{lang_code}",
        ),
        (
            "multiple_parameters",
            "/<string(length=3):lang_code>/<string:id>/<float:probability>",
            "/{lang_code}/{id}/{probability}",
        ),
        (
            "multiple_parameters_varied_length_string",
            "/<string(length=5):lang_code>/<string:id>/<float:probability>",
            "/{lang_code}/{id}/{probability}",
        ),
        (
            "long_path_single_parameter",
            "path/subpath/other_path/<string(length=2):lang_code>",
            "path/subpath/other_path/{lang_code}",
        ),
    ],
)
def test_extract_swagger_path(case_name, test_input, expected):
    assert swagger.extract_swagger_path(test_input) == expected


def test_extract_swagger_path_returns_string():
    assert isinstance(swagger.extract_swagger_path("/endpoint/123"), str)
