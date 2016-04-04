# -*- coding: utf-8 -*-

from __future__ import absolute_import

import functools
import inspect
import re
import six

try:
    # urlparse is renamed to urllib.parse in python 3
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from flask.ext.restful import fields
from flask_restful_swagger import StorageSingleton

from flask_restful_swagger.registry import get_current_registry
from flask_restful_swagger.resources import (
    SwaggerRegistry,
    ResourceLister,
    StaticFiles,
    SwaggerResource,
    SwaggerResourceMeta,
)

from flask_restful_swagger.utils import (
    return_class,
    convert_from_camel_case,
    predicate,
)


# TODO: add pydoc.
def _docs(api,
          api_version='0.0',
          swagger_version='1.2',
          base_path='http://localhost:5000',
          resource_path='/',
          produces="application/json",
          api_spec_url='/api/spec',
          description='Auto generated API docs by flask-restful-swagger'):
    """

    :param api:
    :param api_version:
    :param swagger_version:
    :param base_path:
    :param resource_path:
    :param produces:
    :param api_spec_url:
    :param description:
    :return:
    """
    api_add_resource = api.add_resource

    def add_resource(resource, *urls, **kwargs):
        register_once(
            api, api_add_resource, api_version,
            swagger_version, base_path, resource_path,
            produces, api_spec_url, description,
        )

        resource = return_class(resource)
        # Changed in #pull/92
        for path in urls:
            endpoint = swagger_endpoint(api, resource, path)

            # Add '.help.json' and '.help.html' help urls:
            swagger_path = extract_swagger_path(path)
            endpoint_html_str = '{0}/help'.format(swagger_path)
            # TODO: help.html probably should have a separate endpoint
            # with a unique name, to be accessible within the code.
            api_add_resource(
                endpoint,
                "{0}.help.json".format(swagger_path),
                "{0}.help.html".format(swagger_path),
                endpoint=endpoint_html_str,
            )

        return api_add_resource(resource, *urls, **kwargs)

    api.add_resource = add_resource
    return api


def docs(api, **kwargs):
    """
    This function adds endpoints for the swagger.
    It also handles all the model loading by replacing original `add_resource`
    with the patched one.

        :version changed 1.0.0
        The old docs() function before version 1.0.0 had 'camelCase' kwargs,
        which was not-PEP8, and now it is recommended to use 'snake_case'.
        But for backward compatibility 'cameCase' is also accepted.

    :param api: flask-resful's Api object
    :param kwargs: key-word arguments described in `_docs` function.
    :return: flask-resful's Api object passed as `api`.
    """
    new_kwargs = {convert_from_camel_case(k): v
                  for k, v in six.iteritems(kwargs)}
    return _docs(api, **new_kwargs)


def register_once(api,
                  add_resource_func,
                  api_version,
                  swagger_version,
                  base_path,
                  resource_path,
                  produces,
                  endpoint_path,
                  description):
    def registering_blueprint(setup_state):
        reg = registry[setup_state.blueprint.name]
        reg['x-api-prefix'] = setup_state.url_prefix

    def register_action(name, is_blueprint=True):
        resource_listing_endpoint = StorageSingleton().resource_listing_endpoint

        registry[name] = {
            'apiVersion': api_version,
            'swaggerVersion': swagger_version,
            'basePath': base_path,
            'spec_endpoint_path': endpoint_path,
            'resourcePath': resource_path,
            'produces': produces,
            'description': description,
        }
        if is_blueprint:
            registry[name].update({
                'x-api-prefix': '',
                'apis': [],
            })

            api.blueprint.record(registering_blueprint)

        add_resource_func(
            SwaggerRegistry,
            endpoint_path,
            endpoint_path + '.json',
            endpoint_path + '.html',
            endpoint='app/registry' if not is_blueprint else None,
        )

        resource_listing_endpoint = endpoint_path + '/_/resource_list.json'
        add_resource_func(
            ResourceLister, resource_listing_endpoint,
            endpoint='app/resourcelister' if not is_blueprint else None,
        )

        st = StorageSingleton()
        st.api_spec_static = endpoint_path + '/_/static/'
        add_resource_func(  # TODO: why static path is like this?
            StaticFiles,
            st.api_spec_static + '<string:dir1>/<string:dir2>/<string:dir3>',
            st.api_spec_static + '<string:dir1>/<string:dir2>',
            st.api_spec_static + '<string:dir1>',
            endpoint='app/staticfiles' if not is_blueprint else None,
        )

    registry = StorageSingleton().registry

    if api.blueprint and not registry.get(api.blueprint.name):
        # Most of all this can be taken from the blueprint/app
        register_action(api.blueprint.name, True)
    elif 'app' not in registry:  # review: reuse previous code?
        register_action('app', False)


def swagger_endpoint(api, resource, path):
    endpoint = SwaggerEndpoint(resource, path)
    req_registry = get_current_registry(api=api)
    req_registry.setdefault('apis', []).append(endpoint.__dict__)

    return SwaggerResourceMeta(
        SwaggerResource.__name__,
        SwaggerResource.__bases__,
        dict(SwaggerResource.__dict__),
        _swagger_endpoint=endpoint,
    )


def _sanitize_doc(comment):
    return comment.replace('\n', '<br/>') if comment else comment


def _parse_doc(obj):
    first_line, other_lines = None, None

    full_doc = inspect.getdoc(obj)
    if full_doc:
        line_feed = full_doc.find('\n')
        if line_feed != -1:
            first_line = _sanitize_doc(full_doc[:line_feed])
            other_lines = _sanitize_doc(full_doc[line_feed + 1:])
        else:
            first_line = full_doc

    return first_line, other_lines


class SwaggerEndpoint(object):
    def __init__(self, resource, path):
        self.path = extract_swagger_path(path)
        path_arguments = extract_path_arguments(path)
        self.description, self.notes = _parse_doc(resource)
        self.operations = self.extract_operations(resource, path_arguments)

    @staticmethod
    def extract_operations(resource, path_arguments=None):
        if path_arguments is None:
            path_arguments = []

        operations = []  # review: 4 `for` loops nested? This can be improved.
        for method in resource.methods:
            method_impl = resource.__dict__.get(method.lower(), None)
            if method_impl is None:
                for cls in resource.__mro__:
                    try:
                        method_impl = cls.__dict__[method.lower()]
                    except KeyError:
                        pass

            summary, notes = _parse_doc(method_impl)
            op = {
                'method': method.lower(),
                'parameters': path_arguments,
                'nickname': 'nickname',
                'summary': summary,
                'notes': notes,
            }

            if '__swagger_attr' in method_impl.__dict__:
                # This method was annotated with @swagger.operation
                decorators = method_impl.__dict__['__swagger_attr']

                # bug-fix for:
                # https://github.com/rantav/flask-restful-swagger/issues/90
                primitives = (
                    six.string_types, six.integer_types, list, tuple,
                )

                for att_name, att_value in six.iteritems(decorators):
                    if isinstance(att_value, primitives):
                        if att_name == 'parameters':
                            op['parameters'] = merge_parameter_list(
                                op['parameters'], att_value
                            )
                        else:
                            if op.get(att_name) and att_name is not 'nickname':
                                att_value = '{0}<br/>{1}'.format(
                                    att_value, op[att_name]
                                )
                            op[att_name] = att_value
                    elif hasattr(att_value, '__name__'):
                        op[att_name] = att_value.__name__
                    # TODO: else: raise CustomException
                operations.append(op)
        return operations


def merge_parameter_list(base, override):
    base = list(base)
    names = [x['name'] for x in base]  # TODO: is this required?
    for o in override:
        if o['name'] in names:
            for n, i in enumerate(base):
                if i['name'] == o['name']:
                    base[n] = o
        else:
            base.append(o)
    return base


def operation(**kwargs):
    """
    This decorator marks a function as a swagger operation so that we can easily
    extract attributes from it.
    It saves the decorator's key-values at the function level so we can later
    extract them later when add_resource is invoked.
    """

    def inner(f):
        f.__swagger_attr = kwargs
        return f

    return inner


def model(c=None, *args, **kwargs):
    add_model(c)
    return c


class _Nested(object):
    def __init__(self, klass, **kwargs):
        self._nested = kwargs
        self._klass = klass

    def __call__(self, *args, **kwargs):
        return self._klass(*args, **kwargs)

    def nested(self):
        return self._nested


# wrap _Cache to allow for deferred calling
def nested(klass=None, **kwargs):
    if klass:
        ret = _Nested(klass)
        functools.update_wrapper(ret, klass)
    else:
        def wrapper(klass):
            wrapped = _Nested(klass, **kwargs)
            functools.update_wrapper(wrapped, klass)
            return wrapped

        ret = wrapper
    return ret


def add_model(model_class):
    models = StorageSingleton().registry['models']

    name = model_class.__name__
    model = models[name] = {'id': name}
    model['description'], model['notes'] = _parse_doc(model_class)

    if 'resource_fields' in dir(model_class):
        # We take special care when the model class
        # has a field resource_fields.
        # By convention this field specifies what flask-restful
        # would return when this model is used as a return
        # value from an HTTP endpoint.
        # We look at the class and search for an attribute named
        # resource_fields.
        # If that attribute exists then we deduce the swagger model
        # by the content of this attribute

        if hasattr(model_class, 'required'):
            model['required'] = model_class.required

        properties = model['properties'] = {}

        is_nested = isinstance(model_class, _Nested)
        nested = model_class.nested() if is_nested else {}

        for name, _type in six.iteritems(model_class.resource_fields):
            nested_type = nested[name] if name in nested else None
            properties[name] = deduce_swagger_type(_type, nested_type)

    elif '__init__' in dir(model_class):
        # Alternatively, if a resource_fields does not exist,
        # we deduce the model
        # fields from the parameters sent to its __init__ method

        # Credits for this snippet go to Robin Walsh
        # https://github.com/hobbeswalsh/flask-sillywalk
        argspec = inspect.getargspec(model_class.__init__)
        argspec.args.remove('self')
        defaults = {}
        required = model['required'] = []

        if argspec.defaults:
            defaults = list(
                zip(argspec.args[-len(argspec.defaults):], argspec.defaults)
            )

        properties = model['properties'] = {}
        required_args_count = len(argspec.args) - len(defaults)
        for arg in argspec.args[:required_args_count]:
            required.append(arg)
            # type: string for lack of better knowledge,
            # until we add more metadata
            properties[arg] = {'type': 'string'}
        for k, v in defaults:
            properties[k] = {'type': 'string', 'default': v}

    if 'swagger_metadata' in dir(model_class):
        for field_name, field_metadata in model_class.swagger_metadata.items():
            # does not work for Python 3.x; see: SO
            # how-can-i-merge-two-python-dictionaries-in-a-single-expression
            # properties[field_name] = dict(
            #   properties[field_name].items() + field_metadata.items()
            # )
            if field_name in properties:
                properties[field_name].update(field_metadata)


def deduce_swagger_type(python_type_or_object, nested_type=None):
    # TODO: refactor this
    if predicate(python_type_or_object, (
            str,
            fields.String,
            fields.FormattedString,
            fields.Url,
            int,
            fields.Integer,
            float,
            fields.Float,
            fields.Arbitrary,
            fields.Fixed,
            bool,
            fields.Boolean,
            fields.DateTime,
    )):
        return {'type': deduce_swagger_type_flat(python_type_or_object)}

    if predicate(python_type_or_object, fields.List):
        if inspect.isclass(python_type_or_object):
            return {'type': 'array'}
        else:
            return {
                'type': 'array',
                'items': {
                    '$ref': deduce_swagger_type_flat(
                            python_type_or_object.container, nested_type
                    )
                }
            }
    if predicate(python_type_or_object, fields.Nested):
        return {'type': nested_type}

    return {'type': 'null'}


def deduce_swagger_type_flat(python_type_or_object, nested_type=None):
    if nested_type:
        return nested_type

    if predicate(python_type_or_object, (str,
                                         fields.String,
                                         fields.FormattedString,
                                         fields.Url)):
        return 'string'
    if predicate(python_type_or_object, (int,
                                         fields.Integer)):
        return 'integer'
    if predicate(python_type_or_object, (float,
                                         fields.Float,
                                         fields.Arbitrary,
                                         fields.Fixed)):
        return 'number'
    if predicate(python_type_or_object, (bool,
                                         fields.Boolean)):
        return 'boolean'
    if predicate(python_type_or_object, (fields.DateTime,)):
        return 'date-time'


def extract_swagger_path(path):
    """
    Extracts a swagger type path from the given flask style path.
    This /path/<parameter> turns into this /path/{parameter}
    And this /<string(length=2):lang_code>/<string:id>/<float:probability>
    to this: /{lang_code}/{id}/{probability}
    """
    return re.sub('<(?:[^:]+:)?([^>]+)>', '{\\1}', path)


def extract_path_arguments(path):
    """
    Extracts a swagger path arguments from the given flask path.
    This /path/<parameter> extracts [{name: 'parameter'}]
    And this /<string(length=2):lang_code>/<string:id>/<float:probability>
    extracts: [
    {name: 'lang_code', dataType: 'string'},
    {name: 'id', dataType: 'string'}
    {name: 'probability', dataType: 'float'}]
    """
    # Remove all parentheses
    path = re.sub('\([^\)]*\)', '', path)
    args = re.findall('<([^>]+)>', path)

    def split_arg(arg):
        spl = arg.split(':')
        if len(spl) == 1:
            return {
                'name': spl[0],
                'dataType': 'string',
                'paramType': 'path',
            }
        else:
            return {
                'name': spl[1],
                'dataType': spl[0],
                'paramType': 'path',
            }

    return list(map(split_arg, args))
