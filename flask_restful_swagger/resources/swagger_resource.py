# -*- coding: utf-8 -*-

import six

from flask import request
from flask.ext.restful import Resource

from flask_restful_swagger.utils import render_endpoint

__author__ = 'sobolevn'


class SwaggerResourceMeta(type):
    # noinspection PyInitNewSignature
    def __new__(mcs, name, bases, attributes, _swagger_endpoint=None):
        attributes.update({'swagger_endpoint': _swagger_endpoint})
        return type(name, bases, attributes)


class SwaggerResource(six.with_metaclass(SwaggerResourceMeta, Resource)):
    swagger_endpoint = None

    def get(self):
        if request.path.endswith('.help.json'):
            return self.__class__.swagger_endpoint.__dict__
        if request.path.endswith('.help.html'):
            return render_endpoint(self.__class__.swagger_endpoint)
