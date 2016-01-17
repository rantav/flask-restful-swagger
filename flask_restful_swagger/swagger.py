from flask.ext.restful import Resource


def _create_swagger_endpoint(api):
    class SwaggerEndpoint(Resource):
        def get(self):
            swagger_object = {}
            # filter keys with empty values
            for k, v in api._swagger_object.iteritems():
                if v:
                    swagger_object[k] = v
            return swagger_object

    return SwaggerEndpoint


def doc(operation_object):
    """Decorator to save the documentation of an api endpoint.

    Saves the passed arguments as an attribute to use them later when generating the swagger spec.
    """

    def inner(f):
        f.__swagger_operation_object = {}
        for k, v in operation_object.iteritems():
            if k not in ['tags', 'summary', 'description', 'externalDocs', 'operationId', 'consumes', 'produces',
                         'parameters', 'responses', 'schemes', 'deprecated', 'security']:
                raise ValueError(
                        'The key "{0}" is not specified in the swagger spec. '
                        'See http://swagger.io/specification/#operationObject for a list of valid keys'.format(k))
            f.__swagger_operation_object[k] = v
        return f

    return inner
