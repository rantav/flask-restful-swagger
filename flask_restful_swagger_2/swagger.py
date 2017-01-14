import collections
import re
import inspect
from functools import wraps

from flask import request
from flask_restful import Resource, reqparse, inputs


# python3 compatibility
try:
    basestring
except NameError:
    basestring = str


class ValidationError(ValueError):
    pass


def auth(api_key, endpoint, method):
    """Override this function in your application.

    If this function returns False, 401 forbidden is raised and the documentation is not visible.
    """
    return True


def _auth(*args, **kwargs):
    return auth(*args, **kwargs)


def create_swagger_endpoint(swagger_object):
    """Creates a flask_restful api endpoint for the swagger spec"""

    class SwaggerEndpoint(Resource):
        def get(self):
            swagger_doc = {}
            # filter keys with empty values
            for k, v in swagger_object.items():
                if v or k == 'paths':
                    if k == 'paths':
                        paths = {}
                        for endpoint, view in v.items():
                            views = {}
                            for method, docs in view.items():
                                # check permissions. If a user has not access to an api, do not show the docs of it
                                if auth(request.args.get('api_key'), endpoint, method):
                                    views[method] = docs
                            if views:
                                paths[endpoint] = views
                        swagger_doc['paths'] = collections.OrderedDict(sorted(paths.items()))
                    else:
                        swagger_doc[k] = v
            return swagger_doc

    return SwaggerEndpoint


def set_nested(d, key_spec, value):
    """
    Sets a value in a nested dictionary.
    :param d: The dictionary to set
    :param key_spec: The key specifier in dotted notation
    :param value: The value to set
    """
    keys = key_spec.split('.')

    for key in keys[:-1]:
        d = d.setdefault(key, {})

    d[keys[-1]] = value


def get_data_type(param):
    """
    Maps swagger data types to Python types.
    :param param: swagger parameter
    :return: Python type
    """
    param_type = param.get('type', None)
    if param_type:
        if param_type == 'array':
            param = param['items']
            param_type = param['type']
        if param_type == 'string':
            param_format = param.get('format', None)

            if param_format == 'date':
                return inputs.date

            elif param_format == 'date-time':
                return inputs.datetime_from_iso8601

            return str

        elif param_type == 'integer':
            return int

        elif param_type == 'boolean':
            return inputs.boolean

        elif param_type == 'number':
            param_format = param.get('format', None)

            if param_format == 'float' or param_format == 'double':
                return float

    return None


def get_data_action(param):
    param_type = param.get('type', None)

    if param_type == 'array':
        return 'append'
    return 'store'


def get_parser_arg(param):
    """
    Return an argument for the request parser.
    :param param: Swagger document parameter
    :return: Request parser argument
    """
    return (
        param['name'],
        {
            'dest': param['name'],
            'type': get_data_type(param),
            'location': 'args',
            'help': param.get('description', None),
            'required': param.get('required', False),
            'default': param.get('default', None),
            'action': get_data_action(param)
        })


def get_parser_args(params):
    """
    Return a list of arguments for the request parser.
    :param params: Swagger document parameters
    :return: Request parser arguments
    """
    return [get_parser_arg(p) for p in params if p['in'] == 'query']


def get_parser(params):
    """
    Returns a parser for query parameters from swagger document parameters.
    :param params: swagger doc parameters
    :return: Query parameter parser
    """
    parser = reqparse.RequestParser()

    for arg in get_parser_args(params):
        parser.add_argument(arg[0], **arg[1])

    return parser


def doc(operation_object):
    """Decorator to save the documentation of an api endpoint.

    Saves the passed arguments as an attribute to use them later when generating the swagger spec.
    """
    def decorated(f):
        f.__swagger_operation_object = operation_object

        @wraps(f)
        def inner(self, *args, **kwargs):
            # Get names of resource function arguments

            if hasattr(inspect, 'signature'):
                func_args = list(inspect.signature(f).parameters.keys())
            else:
                func_args = inspect.getargspec(f)[0]

            # Add a parser for query arguments if the special argument '_parser' is present
            if 'parameters' in f.__swagger_operation_object and '_parser' in func_args:
                kwargs.update({'_parser': get_parser(f.__swagger_operation_object['parameters'])})

            return f(self, *args, **kwargs)

        return inner
    return decorated


def validate_path_item_object(path_item_object):
    """Checks if the passed object is valid according to http://swagger.io/specification/#pathItemObject"""

    for k, v in path_item_object.items():
        if k in ['$ref']:
            continue
        if k in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch']:
            validate_operation_object(v)
            continue
        if k in ['parameters']:
            for parameter in v:
                try:
                    validate_reference_object(parameter)
                except ValidationError:
                    validate_parameter_object(parameter)
            continue
        if k.startswith('x-'):
            continue
        raise ValidationError('Invalid path item object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#pathItemObject'))


def validate_operation_object(operation_object):
    for k, v in operation_object.items():
        if k in ['tags', 'consumes', 'produces', 'schemes']:
            if isinstance(v, list):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a list but was "{1}"', k, type(v))
        if k in ['deprecated']:
            if isinstance(v, bool):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a bool but was "{1}"', k, type(v))
        if k in ['summary', 'description', 'operationId']:
            if isinstance(v, basestring):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a string but was "{1}"', k, type(v))
        if k in ['externalDocs']:
            validate_external_documentation_object(v)
            continue
        if k in ['parameters']:
            for parameter in v:
                try:
                    validate_reference_object(parameter)
                except ValidationError:
                    validate_parameter_object(parameter)
            continue
        if k in ['responses']:
            validate_responses_object(v)
            continue
        if k in ['security']:
            validate_security_requirement_object(v)
            continue
        if k.startswith('x-'):
            continue
        raise ValidationError('Invalid operation object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#pathItemObject'))
    if 'responses' not in operation_object:
        raise ValidationError('Invalid operation object. Missing field "responses"')


def validate_parameter_object(parameter_object):
    for k, v in parameter_object.items():
        if k not in ['name', 'in', 'description', 'required', 'schema', 'type', 'format', 'allowEmptyValue', 'items',
                     'collectionFormat', 'default', 'maximum', 'exclusiveMaximum', 'minimum', 'exclusiveMinimum',
                     'maxLength', 'minLength', 'pattern', 'maxItems', 'minItems', 'uniqueItems', 'enum', 'multipleOf']:
            raise ValidationError('Invalid parameter object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#parameterObject'))
    if 'name' not in parameter_object:
        raise ValidationError('Invalid parameter object. Missing field "name"')
    if 'in' not in parameter_object:
        raise ValidationError('Invalid parameter object. Missing field "in"')
    else:
        if parameter_object['in'] not in ['path', 'query', 'header', 'body', 'formData']:
            raise ValidationError(
                    'Invalid parameter object. Value of field "in" must be path, query, header, body or formData, was "{0}"'.format(
                            parameter_object['in']))
        if parameter_object['in'] == 'body':
            if 'schema' not in parameter_object:
                raise ValidationError('Invalid parameter object. Missing field "schema"')
        else:
            if 'type' not in parameter_object:
                raise ValidationError('Invalid parameter object. Missing field "type"')
            if parameter_object['type'] == 'array':
                if 'items' not in parameter_object:
                    raise ValidationError('Invalid parameter object. Missing field "items"')


def validate_reference_object(parameter_object):
    if len(parameter_object.keys()) > 1 or '$ref' not in parameter_object:
        raise ValidationError('Invalid reference object. It may only contain key "$ref"')


def validate_external_documentation_object(external_documentation_object):
    pass


def validate_responses_object(responses_object):
    for k, v in responses_object.items():
        if k.startswith('x-'):
            continue
        try:
            validate_reference_object(v)
        except ValidationError:
            validate_response_object(v)


def validate_response_object(response_object):
    for k, v in response_object.items():
        if k == 'description':
            continue
        if k == 'schema':
            validate_schema_object(v)
            continue
        if k == 'headers':
            validate_headers_object(v)
            continue
        if k == 'examples':
            validate_example_object(v)
            continue
        if k.startswith('x-'):
            continue
        raise ValidationError('Invalid response object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#responseObject'))
    if 'description' not in response_object:
        raise ValidationError('Invalid response object. Missing field "description"')


def validate_security_requirement_object(security_requirement_object):
    pass


def validate_definitions_object(definition_object):
    for k, v in definition_object.items():
        validate_schema_object(v)


def validate_schema_object(schema_object):
    for k, v in schema_object.items():
        if k == 'required' and not isinstance(v, list):
            raise ValidationError('Invalid schema object. "{0}" must be a list but was {1}'.format(k, type(v)))


def validate_headers_object(headers_object):
    pass


def validate_example_object(example_object):
    pass


def extract_swagger_path(path):
    """
    Extracts a swagger type path from the given flask style path.
    This /path/<parameter> turns into this /path/{parameter}
    And this /<string(length=2):lang_code>/<string:id>/<float:probability>
    to this: /{lang_code}/{id}/{probability}
    """
    return re.sub('<(?:[^:]+:)?([^>]+)>', '{\\1}', path)


def sanitize_doc(comment):
    """
    Substitute HTML breaks for new lines in comment text.
    :param comment: The comment text
    :return: Sanitized comment text
    """
    if isinstance(comment, list):
        return sanitize_doc('\n'.join(filter(None, comment)))
    else:
        return comment.replace('\n', '<br/>') if comment else comment


def parse_method_doc(method, operation):
    """
    Parse documentation from a resource method.
    :param method: The resource method
    :param operation: The operation document
    :return: The operation summary
    """
    summary = None

    full_doc = inspect.getdoc(method)
    if full_doc:
        lines = full_doc.split('\n')
        if lines:
            # Append the first line of the docstring to any summary specified
            # in the operation document
            summary = sanitize_doc([operation.get('summary', None), lines[0]])

    return summary


def parse_schema_doc(cls, definition):
    """
    Parse documentation from a schema class.
    :param cls: The schema class
    :param definition: The schema definition
    :return: The schema description
    """
    description = None

    # Skip processing the docstring of the schema class if the schema
    # definition already contains a description
    if 'description' not in definition:
        full_doc = inspect.getdoc(cls)

        # Avoid returning the docstring of the base dict class
        if full_doc and full_doc != inspect.getdoc(dict):
            lines = full_doc.split('\n')
            if lines:
                # Use the first line of the class docstring as the description
                description = sanitize_doc(lines[0])

    return description
