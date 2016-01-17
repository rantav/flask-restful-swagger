from flask.ext.restful import Api as restful_Api

from flask.ext.restful_swagger.swagger import create_swagger_endpoint, validate_path_item_object, ValidationError

class Api(restful_Api):

    def __init__(self, *args, **kwargs):
        self._swagger_object = {
            'swagger': '2.0',
            'info': {
                'title': 'Unnamed',
                'version': kwargs.pop('api_version', '0.0')
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
        api_spec_url = kwargs.pop('api_spec_url', '/api/swagger')
        super(Api, self).__init__(*args, **kwargs)
        if self.app:
            self._swagger_object['info']['title'] = self.app.name
        api_spec_urls = [
            '{0}.json'.format(api_spec_url),
            '{0}.html'.format(api_spec_url),
        ]
        self.add_resource(create_swagger_endpoint(self), *api_spec_urls, endpoint='swagger')

    def add_resource(self, resource, *urls, **kwargs):
        path_item = {}
        for method in [m.lower() for m in resource.methods]:
            f = resource.__dict__.get(method, None)
            swagger_attrs = f.__dict__.get('__swagger_operation_object', None)
            if swagger_attrs:
                path_item[method] = swagger_attrs
        if path_item:
            validate_path_item_object(path_item)
            for url in urls:
                if not url.startswith('/'):
                    raise ValidationError('paths must start with a /')
                self._swagger_object['paths'][url] = path_item
        super(Api, self).add_resource(resource, *urls, **kwargs)
