import pytest

from flask_restful_swagger import swagger


def empty_func():
    pass


def func_with_many_args(arg1, arg2, arg3, kwarg1=None, kwarg2=None):
    allargs = (arg1, arg2, arg3, kwarg1, kwarg2)
    print("func_with_many_args: %s, %s, %s, %s, %s" % allargs)


class EmptyClass:
    pass


@pytest.mark.parametrize(
    "plain_input,swagger_kwargs",
    [
        (empty_func, {"arg1": None, "arg2": None}),
        (func_with_many_args, {"arg1": None, "arg2": None}),
        (EmptyClass, {"arg1": None}),
        (EmptyClass(), {"arg1": None}),
    ],
)
def test_operation(plain_input, swagger_kwargs):
    _add_swagger_attr_wrapper = swagger.operation(**swagger_kwargs)
    swaggered_input = _add_swagger_attr_wrapper(plain_input)

    assert hasattr(swaggered_input, "__swagger_attr")
    assert swaggered_input.__swagger_attr == swagger_kwargs
