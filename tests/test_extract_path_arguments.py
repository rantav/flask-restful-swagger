import pytest

from flask_restful_swagger.swagger import extract_path_arguments
from .lib.helpers import find_nested_func


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/path/with/no/parameters", []),
        (
            "/path/<parameter>",
            [
                {
                    "name": "parameter",
                    "dataType": "string",
                    "paramType": "path",
                },
            ],
        ),
        (
            (
                "/<string(length=2):lang_code>/<string(length=10):identifier>/"
                "<float:probability>"
            ),
            [
                {
                    "name": "lang_code",
                    "dataType": "string",
                    "paramType": "path",
                },
                {
                    "name": "identifier",
                    "dataType": "string",
                    "paramType": "path",
                },
                {
                    "name": "probability",
                    "dataType": "float",
                    "paramType": "path",
                },
            ],
        ),
        (
            (
                "/<string(length=2):lang_code>/<float:identifier>/"
                "<bool:ready_to_proceed>"
            ),
            [
                {
                    "name": "lang_code",
                    "dataType": "string",
                    "paramType": "path",
                },
                {
                    "name": "identifier",
                    "dataType": "float",
                    "paramType": "path",
                },
                {
                    "name": "ready_to_proceed",
                    "dataType": "bool",
                    "paramType": "path",
                },
            ],
        ),
    ],
)
def test_extract_path(path, expected):
    assert extract_path_arguments(path) == expected


@pytest.mark.parametrize(
    "arg,expected",
    [
        (
            "not_declared",
            {
                "name": "not_declared",
                "dataType": "string",
                "paramType": "path",
            },
        ),
        (
            "int:identifier",
            {"name": "identifier", "dataType": "int", "paramType": "path"},
        ),
        (
            "float:amount",
            {"name": "amount", "dataType": "float", "paramType": "path"},
        ),
    ],
)
def test_nested_split_args(arg, expected):
    split_arg = find_nested_func(extract_path_arguments, "split_arg")
    assert split_arg(arg) == expected
