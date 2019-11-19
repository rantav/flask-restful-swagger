from flask_restful_swagger import swagger
import pytest

@pytest.mark.parametrize("testcase_base, testcase_override, testcase_expected_result",
    [([], [], []),
     ([{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" }], 
      [], 
      [{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" }]),
     ([], 
      [{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" }], 
      [{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" }]),
     ([{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" },
       {"method": "BCE", "parameters": "xyz", "nickname": "BCE", "name": "BCE" },
       {"method": "CEF", "parameters": "mnl", "nickname": "CEF", "name": "CEF" },
       {"method": "EFG", "parameters": "rqs", "nickname": "EFG", "name": "EFG" }], 
      [{"method": "FGH", "parameters": "fgh", "nickname": "CEF", "name": "CEF" }], 
      [{'method': 'ABC', 'parameters': 'None', 'nickname': 'ABC', 'name': 'ABC'}, 
       {'method': 'BCE', 'parameters': 'xyz', 'nickname': 'BCE', 'name': 'BCE'}, 
       {'method': 'FGH', 'parameters': 'fgh', 'nickname': 'CEF', 'name': 'CEF'}, 
       {'method': 'EFG', 'parameters': 'rqs', 'nickname': 'EFG', 'name': 'EFG'}]),
     ([{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" }], 
      [{"method": "BCE", "parameters": "xyz", "nickname": "BCE", "name": "BCE" }], 
      [{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" },
       {"method": "BCE", "parameters": "xyz", "nickname": "BCE", "name": "BCE" }]),
      ([{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" },
        {"method": "BCE", "parameters": "xyz", "nickname": "BCE", "name": "BCE" },
        {"method": "CEF", "parameters": "mnl", "nickname": "CEF", "name": "CEF" }], 
       [{"method": "KLM", "parameters": "abc", "nickname": "not my name", "name": "BCE" },
        {"method": "EFG", "parameters": "rqs", "nickname": "EFG", "name": "EFG" }], 
       [{"method": "ABC", "parameters": "None", "nickname": "ABC", "name": "ABC" },
        {"method": "KLM", "parameters": "abc", "nickname": "not my name", "name": "BCE" },
        {"method": "CEF", "parameters": "mnl", "nickname": "CEF", "name": "CEF" },
        {"method": "EFG", "parameters": "rqs", "nickname": "EFG", "name": "EFG" }
        ]),
    ])
def test_merge_parameter_list(testcase_base, testcase_override, testcase_expected_result):
    """This testcase tests the function: merge_parameter_list"""
    assert swagger.merge_parameter_list(testcase_base, testcase_override) == testcase_expected_result
