from flask_restful_swagger import swagger
import types
import pytest


def get_nested_function(outer, innerName, **freeVars):
    """This helper function extracts the code of a function nested within another one"""
    if isinstance(outer, (types.FunctionType, types.MethodType)):
        outer = outer.__code__
        for const in outer.co_consts:
            if isinstance(const, types.CodeType) and const.co_name == innerName:
                return types.FunctionType(const, globals(), None, None, tuple(
                    freeVars(freeVars[name]) for name in const.co_freevars))

@pytest.mark.parametrize("testcase_klass, testcase_kwargs, testcase_ret_funcname",
    [(None, {}, 'wrapper'),
     (None, {"arg1": 1, "arg2": 'Helllllllo!'}, 'wrapper')])
def test_nested(testcase_klass, testcase_kwargs, testcase_ret_funcname):
    """This testcase tests the outside function with no class object: nested"""

    ret = swagger.nested(testcase_klass, **testcase_kwargs)
    assert isinstance(ret, types.FunctionType) and ret.__name__ == testcase_ret_funcname


def test_nested_with_class_object():
    """This testcase tests the outside function with an argument of type class: nested"""
    class A:
        pass

    testcase_klass = A()
    testcase_kwargs = {} 

    ret = swagger.nested(testcase_klass, **testcase_kwargs)
    assert isinstance(ret, swagger._Nested)

