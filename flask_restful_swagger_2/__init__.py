import inspect
import copy

from flask import Blueprint, request
from flask_restful import (Api as restful_Api, abort as flask_abort,
                           Resource as flask_Resource)

from flask_restful_swagger_2.swagger import (ValidationError, create_swagger_endpoint,
                                             add_parameters, validate_path_item_object,
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

        add_parameters(self._swagger_object, kwargs)

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
            if f:
                operation = f.__dict__.get('__swagger_operation_object', None)
                if operation:
                    operation, definitions_ = Extractor.extract(operation)
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
                if self.blueprint and self.blueprint.url_prefix:
                    if not self.blueprint.url_prefix.startswith('/'):
                        raise ValidationError('url_prefix must start with a /')
                    if self.blueprint.url_prefix.endswith('/'):
                        raise ValidationError('url_prefix must not end with a /')
                    url = self.blueprint.url_prefix + url
                self._swagger_object['paths'][extract_swagger_path(url)] = path_item

        super(Api, self).add_resource(resource, *urls, **kwargs)

    def get_swagger_doc(self):
        """Returns the swagger document object."""
        return self._swagger_object


class Extractor(object):
    """
    Extracts swagger.doc object to proper swagger representation by extractor implementation
    """
    @classmethod
    def _choose_impl(cls, operation):
        """
        Chooses implementation of extractor
        """
        if 'reqparser' in operation:
            impl = _RequestParserExtractorImpl
        else:
            impl = _BaseExtractorImpl
        return impl(operation)

    @classmethod
    def extract(cls, operation):
        return cls._choose_impl(operation)._extract()

    def _extract(self):
        raise NotImplementedError()


class _BaseExtractorImpl(Extractor):
    """
    Base implementation of extractor
    Uses for common extraction of swagger.doc
    """
    def __init__(self, operation):
        self._operation = operation

    def _extract(self):
        return self._extract_schemas(self._operation)

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

            obj, definitions = self._extract_model(obj, definitions)

        return obj, definitions

    def _extract_model(self, obj, definitions):
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


class _RequestParserExtractorImpl(_BaseExtractorImpl):
    """
    Uses for extraction of swagger.doc objects, which contains 'reqparser' parameter
    """

    def _extract(self):
        return self._extract_with_reqparser(self._operation)

    def _extract_with_reqparser(self, operation):
        if 'parameters' in operation:
            raise ValidationError('parameters and reqparser can\'t be in same spec')
        # we need to pass copy because 'reqparser' will be deleted
        operation = self._get_reqparse_args(operation.copy())
        return self._extract_schemas(operation)

    def _get_reqparse_args(self, operation):
        """
        Get arguments from specified RequestParser and converts it to swagger representation
        """
        model_data = {'model_name': operation['reqparser']['name'], 'properties': {}, 'required': []}
        make_model = False
        params = []
        for arg in operation['reqparser']['parser'].args:
            if 'json' in arg.location:
                make_model = True
                if arg.required:
                    model_data['required'].append(arg.name)
                model_data['properties'][arg.name] = self._reqparser_arg_to_swagger_param(arg)
            else:
                param = self._reqparser_arg_to_swagger_param(arg)
                # note: "cookies" location not supported by swagger
                if arg.location == 'args':
                    param['in'] = 'query'
                elif arg.location == 'headers':
                    param['in'] = 'header'
                elif arg.location == 'view_args':
                    param['in'] = 'path'
                else:
                    param['in'] = arg.location
                params.append(param)
        del operation['reqparser']

        if make_model:
            model = self.__make_model(**model_data)
            params.append({
                'name': 'body',
                'description': 'Request body',
                'in': 'body',
                'schema': model,
                'required': model.is_required()
            })
        operation['parameters'] = params
        return operation

    @staticmethod
    def _get_swagger_arg_type(type_):
        """
        Converts python-type to swagger type
        If type don't supports, tries to get `swagger_type` property from `type_`
        :param type_:
        :return:
        """
        if hasattr(type_, 'swagger_type'):
            return type_.swagger_type
        elif issubclass(type_, basestring):
            return 'string'
        elif type_ == float:
            return 'float'
        elif type_ == int:
            return 'integer'
        elif type_ == bool:
            return 'boolean'
        elif type_ == bin:
            return 'binary'
        try:
            if type_ == long:
                return 'long'
        except NameError:
            pass
        raise TypeError('unexpected type: {0}'.format(type_))

    @classmethod
    def _reqparser_arg_to_swagger_param(cls, arg):
        """
        Converts particular RequestParser argument to swagger repr
        :param arg:
        :return:
        """
        param = {'name': arg.name,
                 'description': arg.help,
                 'required': arg.required}
        if arg.choices:
            param['enum'] = arg.choices
        if arg.default:
            param['default'] = arg.default
            if callable(param['default']):
                param['default'] = getattr(param['default'], 'swagger_default', None)
        if arg.action == 'append':
            cls.__update_reqparser_arg_as_array(arg, param)
        else:
            param['type'] = cls._get_swagger_arg_type(arg.type)
        return param

    @staticmethod
    def __make_model(**kwargs):
        """
        Creates new `Schema` type, which allows if location of some argument == 'json'
        """
        class _NewModel(Schema):
            pass

        _NewModel.__name__ = kwargs['model_name']
        _NewModel.type = 'object'
        _NewModel.properties = kwargs['properties']
        return _NewModel

    @classmethod
    def __update_reqparser_arg_as_array(cls, arg, param):
        param['items'] = {'type': cls._get_swagger_arg_type(arg.type)}
        param['type'] = 'array'


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

    @classmethod
    def is_required(cls):
        return bool(filter(lambda x: bool(x), map(lambda x: x['required'], cls.properties.values())))


def get_swagger_blueprint(docs, api_spec_url='/api/swagger', **kwargs):
    """
    Returns a Flask blueprint to serve the given list of swagger document objects.
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

    if kwargs:
        add_parameters(swagger_object, kwargs)

    blueprint = Blueprint('swagger', __name__)

    api = restful_Api(blueprint)

    api_spec_urls = [
        '{0}.json'.format(api_spec_url),
        '{0}.html'.format(api_spec_url),
    ]

    api.add_resource(create_swagger_endpoint(swagger_object),
                     *api_spec_urls, endpoint='swagger')

    return blueprint


def swagger_type(type_):
    """Decorator to add __swagger_type property to flask-restful custom input
    type functions
    """

    def inner(f):
        f.__swagger_type = type_
        return f

    return inner
