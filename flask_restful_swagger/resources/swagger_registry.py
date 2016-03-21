# -*- coding: utf-8 -*-

from flask import request
from flask.ext.restful import Resource

from flask_restful_swagger.registry import get_current_registry
from flask_restful_swagger.utils import render_homepage

__author__ = 'sobolevn'


class SwaggerRegistry(Resource):
    def get(self):
        req_registry = get_current_registry()
        if request.path.endswith('.html'):
            return render_homepage(
                    req_registry['basePath'] +
                    req_registry['spec_endpoint_path'] +
                    '/_/resource_list.json'
            )
        return req_registry
