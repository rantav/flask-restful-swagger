import pytest

from flask_restful_swagger import swagger


def test_merge_parameter_list_empty_lists():
    assert swagger.merge_parameter_list([], []) == []


def test_merge_parameter_list_no_changes():
    base = [
        {
            "method": "ABC",
            "parameters": "None",
            "nickname": "ABC",
            "name": "ABC",
        }
    ]
    overrides = []
    assert swagger.merge_parameter_list(base, overrides) == base


@pytest.mark.parametrize(
    "overrides, expected",
    [
        [
            ({"parameters": "None", "name": "ABC"}),
            ({"parameters": "None", "name": "ABC"}),
        ],
        [
            (
                {
                    "method": "GET",
                    "parameters": "Parameters",
                    "nickname": "ABC",
                    "name": "ABC",
                }
            ),
            (
                {
                    "method": "GET",
                    "parameters": "Parameters",
                    "nickname": "ABC",
                    "name": "ABC",
                }
            ),
        ],
        [
            ({"extra_parameter": "something", "name": "ABC"}),
            ({"extra_parameter": "something", "name": "ABC"}),
        ],
        [
            ({"extra_parameter": "something", "name": "ABC"}),
            ({"extra_parameter": "something", "name": "ABC"}),
        ],
    ],
)
def test_merge_parameter_list_with_changes(overrides, expected):
    base = [
        {
            "method": "ABC",
            "parameters": "Some",
            "nickname": "ABC",
            "name": "ABC",
        }
    ]
    assert swagger.merge_parameter_list(base, [overrides]) == [expected]


@pytest.mark.parametrize(
    "overrides, expected",
    [
        [
            [
                {
                    "method": "ABCD",
                    "parameters": "Some",
                    "nickname": "ABCD",
                    "name": "ABCD",
                },
                {
                    "method": "ABC",
                    "parameters": "Some",
                    "nickname": "ABC",
                    "name": "ABC",
                },
            ],
            [
                {
                    "method": "ABC",
                    "parameters": "Some",
                    "nickname": "ABC",
                    "name": "ABC",
                },
                {
                    "method": "ABCDE",
                    "parameters": "Some",
                    "nickname": "ABCDE",
                    "name": "ABCDE",
                },
                {
                    "method": "ABCD",
                    "parameters": "Some",
                    "nickname": "ABCD",
                    "name": "ABCD",
                },
            ],
        ],
    ],
)
def test_merge_parameter_list_appended(overrides, expected):
    base = [
        {
            "method": "ABC",
            "parameters": "Some",
            "nickname": "ABC",
            "name": "ABC",
        },
        {
            "method": "ABCDE",
            "parameters": "Some",
            "nickname": "ABCDE",
            "name": "ABCDE",
        },
    ]
    assert swagger.merge_parameter_list(base, overrides) == expected
