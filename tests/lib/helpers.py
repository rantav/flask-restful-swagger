import sys
from types import CodeType, FunctionType


def find_nested_func(parent, child_name):
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
                return FunctionType(item, globals())
    return None
