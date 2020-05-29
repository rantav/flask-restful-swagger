import sys

from flask import Blueprint, Flask
from flask_restful import Api, Resource

from flask_restful_swagger import swagger
from flask_restful_swagger.swagger import _get_current_registry
from .lib.helpers import TestCaseSupport

tc = TestCaseSupport()
tc.maxDiff = None


def test_get_current_registry_simple():
    app = Flask(__name__)

    with app.test_request_context(path="/some_path.html"):
        registry = _get_current_registry()

    assert registry == {"basePath": "http://localhost", "models": {}}


def test_get_current_registry_request_features():

    app = Flask(__name__)
    app.config["basePath"] = "/abc/123"
    my_blueprint1 = Blueprint("my_blueprint1", __name__)
    api1 = swagger.docs(
        Api(my_blueprint1),
        apiVersion="0.1",
        basePath="http://localhost:5000",
        resourcePath="/",
        produces=["application/json", "text/html"],
        api_spec_url="/api/spec",
        description="Blueprint1 Description",
    )

    class MockResource(Resource):
        @swagger.operation()
        def get(self):
            return "OK", 200, {"Access-Control-Allow-Origin": "*"}

    app.register_blueprint(my_blueprint1, url_prefix="")
    api1.add_resource(MockResource, "/some/urls")

    with app.test_request_context(path="some_path.html"):
        registry = _get_current_registry(api=api1)

    description = (
        "Represents an abstract RESTful resource. " "Concrete resources should"
    )
    notes = (
        "extend from this class and expose methods for each "
        "supported HTTP<br/>method. If a resource is invoked "
        "with an unsupported HTTP method,<br/>the API will "
        "return a response with status 405 Method Not Allowed."
        "<br/>Otherwise the appropriate method is called and "
        "passed all arguments<br/>from the url rule used when "
        "adding the resource to an Api instance. "
        "See<br/>:meth:`~flask_restful.Api.add_resource` "
        "for details."
    )

    if sys.version_info[0] < 3:
        notes = None
        description = None

    tc.assertDictEqual(
        registry,
        {
            "apiVersion": "0.1",
            "swaggerVersion": "1.2",
            "basePath": "http://localhost:5000",
            "spec_endpoint_path": "/api/spec",
            "resourcePath": "/",
            "produces": ["application/json", "text/html"],
            "x-api-prefix": "",
            "apis": [
                {
                    "path": "/some/urls",
                    "description": description,
                    "notes": notes,
                    "operations": [
                        {
                            "method": "get",
                            "nickname": "nickname",
                            "notes": None,
                            "parameters": [],
                            "summary": None,
                        }
                    ],
                }
            ],
            "description": "Blueprint1 Description",
            "models": {},
        },
    )


def test_get_current_registry_request_features_and_docs():
    app = Flask(__name__)
    app.config["basePath"] = "/abc/123"
    my_blueprint1 = Blueprint("my_blueprint1", __name__)
    app.register_blueprint(my_blueprint1, url_prefix="")
    _ = swagger.docs(
        Api(my_blueprint1),
        apiVersion="0.1",
        basePath="http://localhost:5000",
        resourcePath="/",
        produces=["application/json", "text/html"],
        api_spec_url="/api/spec",
        description="Blueprint1 Description",
    )

    with app.test_request_context(path="some_path.html"):
        registry = _get_current_registry()

    tc.assertDictEqual(
        registry,
        {"basePath": "http://localhost", "models": {}}
    )
