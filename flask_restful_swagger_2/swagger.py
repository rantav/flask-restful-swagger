from flask import request
from flask.ext.restful import Resource


class ValidationError(ValueError):
    pass


def auth(api_key, endpoint, method):
    """Override this function in your application.

    If this function returns False, 401 forbidden is raised and the documentation is not visible.
    """
    return True


def _auth(*args, **kwargs):
    return auth(*args, **kwargs)


def create_swagger_endpoint(api):
    """Creates a flask_restful api endpoint for the swagger spec"""

    class SwaggerEndpoint(Resource):
        def get(self):
            swagger_object = {}
            # filter keys with empty values
            for k, v in api._swagger_object.iteritems():
                if v or k == 'paths':
                    if k == 'paths':
                        paths = {}
                        for endpoint, view in v.iteritems():
                            views = {}
                            for method, docs in view.iteritems():
                                # check permissions. If a user has not access to an api, do not show the docs of it
                                if auth(request.args.get('api_key'), endpoint, method):
                                    views[method] = docs
                            if views:
                                paths[endpoint] = views
                        swagger_object['paths'] = paths
                    else:
                        swagger_object[k] = v
            return swagger_object

    return SwaggerEndpoint


def doc(operation_object):
    """Decorator to save the documentation of an api endpoint.

    Saves the passed arguments as an attribute to use them later when generating the swagger spec.
    """

    def inner(f):
        f.__swagger_operation_object = operation_object
        return f

    return inner


def validate_path_item_object(path_item_object):
    """Checks if the passed object is valid according to http://swagger.io/specification/#pathItemObject"""

    for k, v in path_item_object.iteritems():
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
    for k, v in operation_object.iteritems():
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
    if not operation_object.has_key('responses'):
        raise ValidationError('Invalid operation object. Missing field "responses"')


def validate_parameter_object(parameter_object):
    for k, v in parameter_object.iteritems():
        if k not in ['name', 'in', 'description', 'required', 'schema', 'type', 'format', 'allowEmptyValue', 'items',
                     'collectionFormat', 'default', 'maximum', 'exclusiveMaximum', 'minimum', 'exclusiveMinimum',
                     'maxLength', 'minLength', 'pattern', 'maxItems', 'minItems', 'uniqueItems', 'enum', 'multipleOf']:
            raise ValidationError('Invalid parameter object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#parameterObject'))
    if not parameter_object.has_key('name'):
        raise ValidationError('Invalid parameter object. Missing field "name"')
    if not parameter_object.has_key('in'):
        raise ValidationError('Invalid parameter object. Missing field "in"')
    else:
        if parameter_object['in'] == 'body':
            if not parameter_object.has_key('schema'):
                raise ValidationError('Invalid parameter object. Missing field "schema"')
        else:
            if not parameter_object.has_key('type'):
                raise ValidationError('Invalid parameter object. Missing field "type"')
            if parameter_object['type'] == 'array':
                if not parameter_object.has_key('items'):
                    raise ValidationError('Invalid parameter object. Missing field "items"')


def validate_reference_object(parameter_object):
    if len(parameter_object.keys()) > 1 or not parameter_object.has_key('$ref'):
        raise ValidationError('Invalid reference object. It may only contain key "$ref"')


def validate_external_documentation_object(external_documentation_object):
    pass


def validate_responses_object(responses_object):
    for k, v in responses_object.iteritems():
        if k.startswith('x-'):
            continue
        try:
            validate_reference_object(v)
        except ValidationError:
            validate_response_object(v)


def validate_response_object(response_object):
    for k, v in response_object.iteritems():
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
    if not response_object.has_key('description'):
        raise ValidationError('Invalid response object. Missing field "description"')


def validate_security_requirement_object(security_requirement_object):
    pass


def validate_definitions_object(definition_object):
    for k, v in definition_object.iteritems():
        validate_schema_object(v)


def validate_schema_object(schema_object):
    for k, v in schema_object.iteritems():
        if k == 'required' and not isinstance(v, list):
            raise ValidationError('Invalid schema object. "{0}" must a list but was {1}'.format(k, type(v)))


def validate_headers_object(headers_object):
    pass


def validate_example_object(example_object):
    pass
