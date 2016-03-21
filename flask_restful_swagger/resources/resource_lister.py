# -*- coding: utf-8 -*-

from flask.ext.restful import Resource

from flask_restful_swagger.registry import get_current_registry

__author__ = 'sobolevn'


class ResourceLister(Resource):
    def get(self):
        req_registry = get_current_registry()
        path = req_registry['basePath'] + req_registry['spec_endpoint_path']

        return {
            "apiVersion": req_registry['apiVersion'],
            "swaggerVersion": req_registry['swaggerVersion'],
            "apis": [{
                "path": path,
                "description": req_registry['description']
            }]
        }
