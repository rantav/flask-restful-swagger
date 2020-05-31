from flask_restful_swagger.swagger import _Nested


class MockClass(object):
    pass


def mock_function(*args, **kwargs):
    return args, kwargs


def test_nested_class():

    kwargs = {"arg1": 1, "arg2": "Helllllllo!"}

    instance = _Nested(MockClass, **kwargs)

    assert isinstance(instance, _Nested)
    assert instance._klass == MockClass
    assert instance._nested == kwargs
    assert instance.nested() == kwargs


def test_nested_function():

    kwargs = {"arg1": 1, "arg2": "Helllllllo!"}
    args = ("hello", "there")

    instance = _Nested(mock_function, **kwargs)
    value1, value2 = instance(*args, **kwargs)
    assert value1 == args
    assert value2 == kwargs
