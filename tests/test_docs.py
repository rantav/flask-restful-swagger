import types

from flask import Blueprint, Flask
from flask_restful import Api, Resource

from flask_restful_swagger.swagger import docs

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

docs_kwargs = {
    "apiVersion": "an api version",
    "basePath": "a basepath",
    "resourcePath": "a resource path",
    "produces": ["application/json", "text/html"],
    "api_spec_url": "an api spec url",
    "description": "an Api Description Description",
}


def test_docs_simple_instantiate():

    app = Flask(__name__)
    app.config["basePath"] = "/abc/123"
    my_blueprint1 = Blueprint("my_blueprint1", __name__)

    api1 = docs(Api(my_blueprint1), **docs_kwargs)

    assert api1.add_resource.__name__ == "add_resource"
    assert isinstance(api1.add_resource, types.FunctionType)


@patch("flask_restful_swagger.swagger.register_once")
@patch("flask_restful_swagger.swagger.make_class")
@patch("flask_restful_swagger.swagger.swagger_endpoint")
@patch("flask_restful_swagger.swagger.extract_swagger_path")
def test_docs_simple_instantiate_add_resources(
    path, endpoint, make_class, register
):

    my_blueprint1 = Blueprint("my_blueprint1", __name__)

    api1 = docs(Api(my_blueprint1), **docs_kwargs)

    class MockResource(Resource):
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    make_class.return_value = MockResource
    endpoint.return_value = MockResource
    path.return_value = "/some/swagger/path"

    api1.add_resource(MockResource, "/some/url")

    # Validate All Mock Calls

    assert register.call_args_list[0][0][0] == api1
    assert register.call_args_list[0][0][2:] == (
        "an api version",
        "1.2",
        "a basepath",
        "a resource path",
        ["application/json", "text/html"],
        "an api spec url",
        "an Api Description Description",
    )
    assert len(register.call_args_list[0][0]) == 9

    path.assert_called_once_with("/some/url")
    assert endpoint.call_args_list[0][0][0] == api1
    assert endpoint.call_args_list[0][0][2] == "/some/url"
    make_class.assert_called_once_with(MockResource)
