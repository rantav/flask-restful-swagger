# -*- coding: utf-8 -*-

import os
import mimetypes

from flask import abort, Response
from flask.ext.restful import Resource
from flask_restful_swagger import root_path

from flask_restful_swagger.registry import get_current_registry
from flask_restful_swagger.utils import render_page

__author__ = 'sobolevn'


class StaticFiles(Resource):
    # TODO: is it possible to change this signature?
    def get(self, dir1=None, dir2=None, dir3=None):
        req_registry = get_current_registry()

        if dir1 is None:
            filePath = "index.html"
        else:  # TODO: this can be improved
            # Try something like:
            # '/'.join(v.strip('/') for k, v in kwargs.items() if v is not None)
            filePath = dir1
            if dir2 is not None:
                filePath = "%s/%s" % (filePath, dir2)
                if dir3 is not None:
                    filePath = "%s/%s" % (filePath, dir3)

        if filePath in [
            "index.html",
            "o2c.html",
            "swagger-ui.js",
            "swagger-ui.min.js",
            "lib/swagger-oauth.js",
        ]:
            conf = {'resource_list_url': req_registry['spec_endpoint_path']}
            return render_page(filePath, conf)

        mime = mimetypes.guess_type(filePath)[0]

        file_path = os.path.join(root_path, 'static', filePath)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fs:
                return Response(fs, mimetype=mime)
        abort(404)
