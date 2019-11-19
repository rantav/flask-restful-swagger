from flask_restful_swagger import swagger
from unittest.mock import Mock, patch
import types
import pytest


def test_documentation_example():

    """ This test case tests the outside function extract_path_arguments using
        the example given in the documentation
    """
    path = '/<string(length=2):lang_code>/<string:id>/<float:probability>'
    expected_result = [{"name": 'lang_code', "dataType": 'string', "paramType": "path"},
                       {"name": 'id', "dataType": 'string', "paramType": "path"},
                       {"name": 'probability', "dataType": 'float', "paramType": "path"}]

    ret_result = swagger.extract_path_arguments(path)
    assert ret_result == expected_result


def get_nested_function(outer, innerName, **freeVars):
    """This helper function extracts the code of a function nested within another one"""
    if isinstance(outer, (types.FunctionType, types.MethodType)):
        outer = outer.__code__
        for const in outer.co_consts:
            if isinstance(const, types.CodeType) and const.co_name == innerName:
                return types.FunctionType(const, globals(), None, None, tuple(
                    freeVars(freeVars[name]) for name in const.co_freevars))


@pytest.mark.parametrize("testcase_string,testcase_expected_result",
    [('HelloWorld', {"name": 'HelloWorld', "dataType": 'string', "paramType": "path"}),
     ('Hello:World', {"name": 'World', "dataType": 'Hello', "paramType": "path"})])
def test_split_arg(testcase_string, testcase_expected_result):
    """This testcase tests the outside function: extract_path_arguments"""
    temp_split_arg = get_nested_function(swagger.extract_path_arguments, 'split_arg')
    assert temp_split_arg(testcase_string) == testcase_expected_result
