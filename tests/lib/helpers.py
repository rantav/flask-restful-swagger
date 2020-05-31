import sys
from types import CodeType, FunctionType
from unittest import TestCase


def freeVar(val):
    def nested():
        return val

    return nested.__closure__[0]


def find_nested_func(parent, child_name, **kwargs):
    """Returns a function nested inside another function.
    :param parent: The parent function to search inside.
    :type parent: func
    :param child_name: A string containing the name of the child function.
    :type child_name: string
    :returns: The nested function, or None
    """
    if sys.version_info[0] < 3:
        consts = parent.func_code.co_consts
    else:
        consts = parent.__code__.co_consts
    for item in consts:
        if isinstance(item, CodeType):
            if item.co_name == child_name:
                return FunctionType(
                    item,
                    globals(),
                    None,
                    None,
                    tuple(freeVar(name) for name in item.co_freevars),
                )
    return None


class TestCaseSupport(TestCase):
    def runTest(self):
        pass
