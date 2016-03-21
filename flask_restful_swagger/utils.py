# -*- coding: utf-8 -*-

import functools
import warnings
import re
import inspect
import os
import mimetypes

from flask import Response
from jinja2 import Template

from flask_restful_swagger import api_spec_static, root_path, templates

__author__ = 'sobolevn'


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    :param func: function to decorated.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1,
        )
        return func(*args, **kwargs)

    return new_func


def convert_from_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def render_endpoint(endpoint):
    return render_page("endpoint.html", endpoint.__dict__)


def render_homepage(resource_list_url):
    conf = {'resource_list_url': resource_list_url}
    return render_page("index.html", conf)


def render_page(page, info):
    from flask_restful_swagger.registry import get_current_registry

    global templates

    req_registry = get_current_registry()
    url = req_registry['basePath']
    if url.endswith('/'):
        url = url.rstrip('/')
    conf = {
        'base_url': url + api_spec_static,
        'full_base_url': url + api_spec_static
    }
    if info is not None:
        conf.update(info)

    if page in templates:
        template = templates[page]
    else:
        with open(os.path.join(root_path, 'static', page), 'r') as fs:
            template = Template(fs.read())
            templates[page] = template

    mime = mimetypes.guess_type(page)[0]
    return Response(template.render(conf), mimetype=mime)


def return_class(class_or_instance):
    if inspect.isclass(class_or_instance):
        return class_or_instance
    return class_or_instance.__class__


def predicate(python_type_or_object, types):
    if inspect.isclass(python_type_or_object):
        inner = issubclass
    else:
        inner = isinstance

    return inner(python_type_or_object, types)
