# -*- coding: utf-8 -*-

import os
import mimetypes

from flask import abort, send_file
from flask.ext.restful import Resource
from flask_restful_swagger import root_path

from flask_restful_swagger.registry import get_current_registry
from flask_restful_swagger.utils import render_page

__author__ = 'sobolevn'


class StaticFiles(Resource):
    # TODO: is it possible to change this signature?
    def get(self, **kwargs):
        req_registry = get_current_registry()

        if not kwargs:
            file_path = "index.html"
        else:
            keys = sorted(kwargs.keys())
            file_path = '/'.join(
                kwargs[k].strip('/') for k in keys if kwargs[k] is not None
            )

        if file_path in [  # TODO: refactor to TemplateResource
            "index.html",
            "o2c.html",
            "swagger-ui.js",
            "swagger-ui.min.js",
            "lib/swagger-oauth.js",
        ]:
            conf = {'resource_list_url': req_registry['spec_endpoint_path']}
            return render_page(file_path, conf)

        mime = mimetypes.guess_type(file_path)[0]

        file_path = os.path.join(root_path, 'static', file_path)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype=mime)
        abort(404)
