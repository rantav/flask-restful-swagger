from flask_restful_swagger import swagger
"""
  Docstring from extract_swagger_path:

  Extracts a swagger type path from the given flask style path.
  This /path/<parameter> turns into this /path/{parameter}
  And this /<string(length=2):lang_code>/<string:id>/<float:probability>
  to this: /{lang_code}/{id}/{probability}
  """

def test_extract_swagger_path_empty_string():
    assert swagger.extract_swagger_path('') == ''

def test_extract_swagger_path_simple():
    assert swagger.extract_swagger_path('/endpoint') == '/endpoint'

def test_extract_swagger_path_single_parameter_no_type():
    assert swagger.extract_swagger_path('/path/<parameter>') == '/path/{parameter}'

def test_extract_swagger_path_single_parameter_string():
    assert swagger.extract_swagger_path('/<string(length=2):lang_code>') == '/{lang_code}'

def test_extract_swagger_path_multiple_parameters():
    assert swagger.extract_swagger_path('/<string(length=2):lang_code>/<string:id>/<float:probability>') == '/{lang_code}/{id}/{probability}'

def test_extract_swagger_path_long_path_single_parameter():
    assert swagger.extract_swagger_path('path/subpath/other_path/<string(length=2):lang_code>') == 'path/subpath/other_path/{lang_code}'
