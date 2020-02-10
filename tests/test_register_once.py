from flask import Blueprint
from flask_restful import Api

import flask_restful_swagger
from .lib.helpers import find_nested_func


class MockRegistration:
    def __init__(self):
        self.args = []
        self.kwargs = []

    def reset(self):
        self.args = []
        self.kwargs = []

    def add(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)


class MockState(object):
    def __init__(self, blueprint=None, url_prefix=None):
        self.blueprint = blueprint
        self.url_prefix = url_prefix


mock_registration = MockRegistration()


register_once_kwargs = {
    "add_resource_func": mock_registration.add,
    "apiVersion": "0.1",
    "swaggerVersion": "1.2",
    "basePath": "https://localhost:5000",
    "resourcePath": "/api/spec",
    "produces": ["application/json"],
    "endpoint_path": "/endpoint",
    "description": "Mock API Registry Data",
}

registry_content_for_test = {
    "apiVersion": "0.1",
    "swaggerVersion": "1.2",
    "basePath": "https://localhost:5000",
    "spec_endpoint_path": "/endpoint",
    "resourcePath": "/api/spec",
    "produces": ["application/json"],
    "x-api-prefix": "",
    "apis": [],
    "description": "Mock API Registry Data",
}


def test_register_once_blueprint():

    mock_registration.reset()

    if "app" in flask_restful_swagger.registry:
        del flask_restful_swagger.registry["app"]

    my_blueprint1 = Blueprint("test", __name__)
    api = Api(my_blueprint1)

    kwargs = dict(register_once_kwargs)
    kwargs["api"] = api

    flask_restful_swagger.swagger.register_once(**kwargs)
    assert flask_restful_swagger.registry["test"] == registry_content_for_test
    flask_restful_swagger.swagger.register_once(**kwargs)
    assert flask_restful_swagger.registry["test"] == registry_content_for_test

    assert mock_registration.args == [
        (
            flask_restful_swagger.swagger.SwaggerRegistry,
            "/endpoint",
            "/endpoint.json",
            "/endpoint.html",
        ),
        (
            flask_restful_swagger.swagger.ResourceLister,
            "/endpoint/_/resource_list.json",
        ),
        (
            flask_restful_swagger.swagger.StaticFiles,
            "/endpoint/_/static/<string:dir1>/<string:dir2>/<string:dir3>",
            "/endpoint/_/static/<string:dir1>/<string:dir2>",
            "/endpoint/_/static/<string:dir1>",
        ),
        (
            flask_restful_swagger.swagger.SwaggerRegistry,
            "/endpoint",
            "/endpoint.json",
            "/endpoint.html",
        ),
        (
            flask_restful_swagger.swagger.ResourceLister,
            "/endpoint/_/resource_list.json",
        ),
        (
            flask_restful_swagger.swagger.StaticFiles,
            "/endpoint/_/static/<string:dir1>/<string:dir2>/<string:dir3>",
            "/endpoint/_/static/<string:dir1>/<string:dir2>",
            "/endpoint/_/static/<string:dir1>",
        ),
    ]
    assert mock_registration.kwargs == [
        {},
        {},
        {},
        {"endpoint": "app/registry"},
        {"endpoint": "app/resourcelister"},
        {"endpoint": "app/staticfiles"},
    ]


def test_register_once_without_blueprint():

    mock_registration.reset()

    if "app" in flask_restful_swagger.registry:
        del flask_restful_swagger.registry["app"]

    api = Api()
    kwargs = dict(register_once_kwargs)
    kwargs["api"] = api

    flask_restful_swagger.swagger.register_once(**kwargs)
    assert flask_restful_swagger.registry["test"] == registry_content_for_test
    flask_restful_swagger.swagger.register_once(**kwargs)
    assert flask_restful_swagger.registry["test"] == registry_content_for_test

    assert mock_registration.args == [
        (
            flask_restful_swagger.swagger.SwaggerRegistry,
            "/endpoint",
            "/endpoint.json",
            "/endpoint.html",
        ),
        (
            flask_restful_swagger.swagger.ResourceLister,
            "/endpoint/_/resource_list.json",
        ),
        (
            flask_restful_swagger.swagger.StaticFiles,
            "/endpoint/_/static/<string:dir1>/<string:dir2>/<string:dir3>",
            "/endpoint/_/static/<string:dir1>/<string:dir2>",
            "/endpoint/_/static/<string:dir1>",
        ),
    ]

    assert mock_registration.kwargs == [
        {"endpoint": "app/registry"},
        {"endpoint": "app/resourcelister"},
        {"endpoint": "app/staticfiles"},
    ]


def test_register_test_deferred_setup():

    if "app" in flask_restful_swagger.registry:
        del flask_restful_swagger.registry["app"]
    if "registered_blueprint" in flask_restful_swagger.registry:
        del flask_restful_swagger.registry["registered_blueprint"]

    blueprint = Blueprint("registered_blueprint", __name__)
    api = Api(blueprint)

    kwargs = dict(register_once_kwargs)
    kwargs["api"] = api

    flask_restful_swagger.swagger.register_once(**kwargs)

    assert (
        flask_restful_swagger.registry["registered_blueprint"]["x-api-prefix"]
        == ""
    )

    func = find_nested_func(
        flask_restful_swagger.swagger.register_once, "registering_blueprint"
    )
    state = MockState(blueprint=blueprint, url_prefix="/none")

    func.__globals__["registry"] = flask_restful_swagger.registry
    func(state)

    assert (
        flask_restful_swagger.registry["registered_blueprint"]["x-api-prefix"]
        == "/none"
    )
