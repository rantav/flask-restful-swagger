from flask.ext.restful import Resource
import inspect
from flask_restful_swagger import registry, registered


def docs(api, apiVersion='0.0', swaggerVersion='1.2'):

  api_add_resource = api.add_resource
  def add_resource(resource, path, *args, **kvargs):
    endpoint = "%s_help" % resource.__name__
    api_add_resource(swagger_endpoint(resource, path), "%s.help.json" % path, endpoint=endpoint)
    # TODO: Add an HTML endpoint
    # api_add_resource(swagger_endpoint(resource, path), "%s.help.html" % path, endpoint=endpoint)
    register_once(api_add_resource, apiVersion, swaggerVersion)
    return api_add_resource(resource, path, *args, **kvargs)
  api.add_resource = add_resource

  return api

def register_once(add_resource, apiVersion, swaggerVersion):
  global registered
  if not registered:
    registered = True
    registry['apiVersion'] = apiVersion
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
        for name, value in decorators.items():
          if isinstance(value, (basestring, int, list)):
            op[name] = value
          else:
            op[name] = value.__name__

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

def model(c, *args, **kwargs):
  def inner(*args, **kwargs):
    # c.__swagger_attr = kwargs
    return c(*args, **kwargs)

  models = registry['models']
  name = c.__name__
  model = models[name] = {'id': name}
  if '__init__' in dir(c):
    # Credits for this snippet go to Robin Walsh
    # https://github.com/hobbeswalsh/flask-sillywalk
    argspec = inspect.getargspec(c.__init__)
    argspec.args.remove("self")
    defaults = {}
    required = model['required'] = []
    if argspec.defaults:
      defaults = zip(argspec.args[-len(argspec.defaults):], argspec.defaults)
    properties = model['properties'] = {}
    for arg in argspec.args[:-len(defaults)]:
      required.append(arg)
      # properties[arg] = {"required": True}
    for k, v in defaults:
      properties[k] = {"default": v}

  return inner
