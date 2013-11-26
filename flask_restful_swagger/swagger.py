from flask.ext.restful import reqparse, abort, Api, Resource

registry = {
  'apis': []
}
registered = False

def docs(api, version='0.0', swaggerVersion='1.2'):

  api_add_resource = api.add_resource
  def add_resource(resource, path, *args, **kvargs):
    endpoint = "%s_help" % resource.__name__
    api_add_resource(swagger_endpoint(resource, path), "%s.help.json" % path, endpoint=endpoint)
    # TODO: Add an HTML endpoint
    # api_add_resource(swagger_endpoint(resource, path), "%s.help.html" % path, endpoint=endpoint)
    register_once(api_add_resource, version, swaggerVersion)
    return api_add_resource(resource, path, *args, **kvargs)
  api.add_resource = add_resource

  return api

def register_once(add_resource, version, swaggerVersion):
  global registered
  if not registered:
    registered = True
    registry['apiVersion'] = version
    registry['swaggerVersion'] = swaggerVersion
    add_resource(SwaggerRegistry, '/resources.json')

def swagger_endpoint(resource, path):
  registry['apis'].append(SwaggerEndpoint(resource, path).__dict__)
  class SwaggerResource(Resource):
    def get(self, *args, **kvargs):
      return {
        'args': args,
        'kvargs': kvargs,
        'path': path
      }
  return SwaggerResource

class SwaggerEndpoint(object):
  def __init__(self, resource, path):
    self.path = path
    if not resource.__doc__  is None: self.description = resource.__doc__
    self.operations = self.extract_operations(resource)

  @staticmethod
  def extract_operations(resource):
    operations = []
    for method in resource.methods:
      method_impl = resource.__dict__[method.lower()]
      op = {
          'method': method
      }
      if method_impl.__doc__ is not None:
        op['summary'] = method_impl.__doc__
      if '__swagger_attr' in method_impl.__dict__:
        decorators = method_impl.__dict__['__swagger_attr']
        if decorators['notes']: op['notes'] = decorators['notes']
      operations.append(op)
    return operations

class SwaggerRegistry(Resource):
  def get(self):
    return registry

def operation(**kwargs):
  def inner(f):
    f.__swagger_attr = kwargs
    return f
  return inner