import inspect
import copy

from flask import Blueprint, request
from flask_restful import (Api as restful_Api, abort as flask_abort,
                           Resource as flask_Resource)

from flask_restful_swagger_2.swagger import (ValidationError, create_swagger_endpoint,
                                             set_nested, validate_path_item_object,
                                             validate_operation_object,
                                             validate_definitions_object,
                                             extract_swagger_path, parse_method_doc,
                                             parse_schema_doc, _auth as auth)


# python3 compatibility
try:
    basestring
except NameError:
    basestring = str


def abort(http_status_code, schema=None, **kwargs):
    if schema:
        kwargs.update(schema)
    flask_abort(http_status_code, **kwargs)


class ModelError(Exception):
    pass


def auth_required(f):
    """Decorator which checks if the request is permitted to call the view"""

    def decorator(*args, **kwargs):
        if not auth(request.args.get('api_key'), extract_swagger_path(request.url_rule.rule), request.method):
            abort(401)
        return f(*args, **kwargs)

    return decorator


class Resource(flask_Resource):
    decorators = [auth_required]


class Api(restful_Api):
    def __init__(self, *args, **kwargs):
        api_spec_base = kwargs.pop('api_spec_base', None)

        self._swagger_object = {
            'swagger': '2.0',
            'info': {
                'title': '',
                'description': '',
                'termsOfService': '',
                'version': '0.0'
            },
            'host': '',
            'basePath': '',
            'schemes': [],
            'consumes': [],
            'produces': [],
            'paths': {},
            'definitions': {},
            'parameters': {},
            'responses': {},
            'securityDefinitions': {},
            'security': [],
            'tags': [],
            'externalDocs': {}
        }

        if api_spec_base is not None:
            self._swagger_object = copy.deepcopy(api_spec_base)

        # A list of accepted parameters.  The first item in the tuple is the
        # name of keyword argument, the second item is the default value,
        # and the third item is the key name in the swagger object.
        params = [
            ('title', '', 'info.title'),
            ('description', '', 'info.description'),
            ('terms', '', 'info.termsOfService'),
            ('api_version', '', 'info.version'),
            ('contact', {}, 'info.contact'),
            ('license', {}, 'info.license'),
            ('host', '', 'host'),
            ('base_path', '', 'basePath'),
            ('schemes', [], 'schemes'),
            ('consumes', [], 'consumes'),
            ('produces', [], 'produces'),
            ('parameters', {}, 'parameters'),
            ('responses', {}, 'responses'),
            ('security_definitions', {}, 'securityDefinitions'),
            ('security', [], 'security'),
            ('tags', [], 'tags'),
            ('external_docs', {}, 'externalDocs'),
        ]

        for param in params:
            value = kwargs.pop(param[0], param[1])
            if value:
                set_nested(self._swagger_object, param[2], value)

        api_spec_url = kwargs.pop('api_spec_url', '/api/swagger')
        add_api_spec_resource = kwargs.pop('add_api_spec_resource', True)

        super(Api, self).__init__(*args, **kwargs)

        if self.app and not self._swagger_object['info']['title']:
            self._swagger_object['info']['title'] = self.app.name

        # Unless told otherwise, create and register the swagger endpoint
        if add_api_spec_resource:
            api_spec_urls = [
                '{0}.json'.format(api_spec_url),
                '{0}.html'.format(api_spec_url),
            ]

            self.add_resource(create_swagger_endpoint(self.get_swagger_doc()),
                              *api_spec_urls, endpoint='swagger')

    def add_resource(self, resource, *urls, **kwargs):
        path_item = {}
        definitions = {}

        for method in [m.lower() for m in resource.methods]:
            f = resource.__dict__.get(method, None)
            operation = f.__dict__.get('__swagger_operation_object', None)
            if operation:
                operation, definitions_ = self._extract_schemas(operation)
                path_item[method] = operation
                definitions.update(definitions_)
                summary = parse_method_doc(f, operation)
                if summary:
                    operation['summary'] = summary

        validate_definitions_object(definitions)
        self._swagger_object['definitions'].update(definitions)

        if path_item:
            validate_path_item_object(path_item)
            for url in urls:
                if not url.startswith('/'):
                    raise ValidationError('paths must start with a /')
                self._swagger_object['paths'][extract_swagger_path(url)] = path_item

        super(Api, self).add_resource(resource, *urls, **kwargs)

    def get_swagger_doc(self):
        """Returns the swagger document object."""
        return self._swagger_object

    def _extract_schemas(self, obj):
        """Converts all schemes in a given object to its proper swagger representation."""
        definitions = {}
        if isinstance(obj, list):
            for i, o in enumerate(obj):
                obj[i], definitions_ = self._extract_schemas(o)
                definitions.update(definitions_)

        if isinstance(obj, dict):
            for k, v in obj.items():
                obj[k], definitions_ = self._extract_schemas(v)
                definitions.update(definitions_)

        if inspect.isclass(obj):
            # Object is a model. Convert it to valid json and get a definition object
            if not issubclass(obj, Schema):
                raise ValueError('"{0}" is not a subclass of the schema model'.format(obj))
            definition = obj.definitions()
            description = parse_schema_doc(obj, definition)
            if description:
                definition['description'] = description
            # The definition itself might contain models, so extract them again
            definition, additional_definitions = self._extract_schemas(definition)
            definitions[obj.__name__] = definition
            definitions.update(additional_definitions)
            obj = obj.reference()

        return obj, definitions


class Schema(dict):
    properties = None

    def __init__(self, **kwargs):
        if self.properties:
            for k, v in kwargs.items():
                if k not in self.properties:
                    raise ValueError(
                            'The model "{0}" does not have an attribute "{1}"'.format(self.__class__.__name__, k))
                if 'type' in self.properties[k]:
                    type_ = self.properties[k]['type']
                    if type_ == 'integer' and not isinstance(v, int):
                        raise ValueError('The attribute "{0}" must be an int, but was "{1}"'.format(k, type(v)))
                    if type_ == 'number' and not isinstance(v, int) and not isinstance(v, float):
                        raise ValueError(
                                'The attribute "{0}" must be an int or float, but was "{1}"'.format(k, type(v)))
                    if type_ == 'string' and not isinstance(v, basestring):
                        raise ValueError('The attribute "{0}" must be a string, but was "{1}"'.format(k, type(v)))
                    if type_ == 'boolean' and not isinstance(v, bool):
                        raise ValueError('The attribute "{0}" must be an int, but was "{1}"'.format(k, type(v)))
                self[k] = v

        if hasattr(self, 'required'):
            for key in self.required:
                if key not in kwargs:
                    raise ValueError('The attribute "{0}" is required'.format(key))

    @classmethod
    def reference(cls):
        return {'$ref': '#/definitions/{0}'.format(cls.__name__)}

    @classmethod
    def definitions(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}

    @classmethod
    def array(cls):
        return {'type': 'array', 'items': cls}


def get_swagger_blueprint(docs, api_spec_url='/api/swagger'):
    """
    Returns a Flsk blueprint to serve the given list of swagger document objects.
    :param docs: A list of of swagger document objects
    :param api_spec_url: The URL path that serves the swagger specification document
    :return: A Flask blueprint
    """
    swagger_object = {}
    paths = {}
    definitions = {}

    for doc in docs:
        # Paths and definitions are appended, but overwrite other fields
        if 'paths' in doc:
            paths.update(doc['paths'])

        if 'definitions' in doc:
            definitions.update(doc['definitions'])

        swagger_object.update(doc)

    swagger_object['paths'] = paths
    swagger_object['definitions'] = definitions

    blueprint = Blueprint('swagger', __name__)

    api = restful_Api(blueprint)

    api_spec_urls = [
        '{0}.json'.format(api_spec_url),
        '{0}.html'.format(api_spec_url),
    ]

    api.add_resource(create_swagger_endpoint(swagger_object),
                     *api_spec_urls, endpoint='swagger')

    return blueprint
