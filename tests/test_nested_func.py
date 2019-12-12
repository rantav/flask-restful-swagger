import types

import pytest

from flask_restful_swagger.swagger import _Nested, nested


class MockClass(object):
    pass


def test_nested_without_a_class():
    ret = nested(None, kwargs={"arg1": 1, "arg2": "Helllllllo!"})
    assert isinstance(ret, types.FunctionType)
    assert ret.__name__ == "wrapper"


def test_wrapped_object_is_correct():
    ret = nested(klass=None, kwargs={"arg1": 1, "arg2": "Helllllllo!"})
    resolved = ret(MockClass)
    assert isinstance(resolved, _Nested)
    assert isinstance(resolved, _Nested)


@pytest.mark.parametrize(
    "testcase_klass, testcase_kwargs",
    [(MockClass, {}), (MockClass, {"arg1": 1, "arg2": "Helllllllo!"})],
)
def test_nested_with_a_class(testcase_klass, testcase_kwargs):
    ret = nested(klass=testcase_klass, **testcase_kwargs)
    assert isinstance(ret, _Nested)
    assert ret._klass == MockClass
