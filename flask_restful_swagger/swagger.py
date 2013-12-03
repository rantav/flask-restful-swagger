from flask.ext.restful import Resource
import inspect
import functools
import re
from flask_restful_swagger import registry, registered


def docs(api, apiVersion='0.0', swaggerVersion='1.2',
         basePath='http://localhost:5000',
         resourcePath='/', produces=["application/json"]):

  api_add_resource = api.add_resource

  def add_resource(resource, path, *args, **kvargs):
    endpoint = swagger_endpoint(resource, path)
    # TODO: Add a nice JSON help url
    # endpoint_path = "%s_help" % resource.__name__
    # api_add_resource(endpoint, "%s.help.json" % path,
    #                  endpoint=endpoint_path)
    # TODO: Add a nice HTML help url
    # api_add_resource(endpoint, "%s.help.html" % path,
    #                  endpoint_=endpoint_path)
    register_once(api_add_resource, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces)
    return api_add_resource(resource, path, *args, **kvargs)
  api.add_resource = add_resource

  return api


def register_once(add_resource, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces):
  global registered
  if not registered:
    registered = True
    registry['apiVersion'] = apiVersion
    registry['swaggerVersion'] = swaggerVersion
    registry['basePath'] = basePath
    registry['resourcePath'] = resourcePath
    registry['produces'] = produces
    add_resource(SwaggerRegistry, '/api/spec.json')


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
    self.path = extract_swagger_path(path)
    path_arguments = extract_path_arguments(path)
    if not resource.__doc__ is None:
      self.description = resource.__doc__
    self.operations = self.extract_operations(resource, path_arguments)

  @staticmethod
  def extract_operations(resource, path_arguments=[]):
    operations = []
    for method in resource.methods:
      method_impl = resource.__dict__[method.lower()]
      op = {
          'method': method,
          'parameters': path_arguments,
          'nickname': 'nickname'
      }
      if method_impl.__doc__ is not None:
        op['summary'] = method_impl.__doc__
      if '__swagger_attr' in method_impl.__dict__:
        # This method was annotated with @swagger.operation
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
  """
  This dedorator marks a function as a swagger operation so that we can easily
  extract attributes from it.
  It saves the decorator's key-values at the function level so we can later
  extract them later when add_resource is invoked.
  """
  def inner(f):
    f.__swagger_attr = kwargs
    return f
  return inner


def model(c, *args, **kwargs):

  def inner(*args, **kwargs):
    return c(*args, **kwargs)

  functools.update_wrapper(inner, c)
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
      # type: string for lack of better knowledge, until we add more metadata
      properties[arg] = {'type': 'string'}
    for k, v in defaults:
      properties[k] = {'type': 'string', "default": v}

  return inner


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
  # Remove all paranteses
  path = re.sub('\([^\)]*\)', '', path)
  args = re.findall('<([^>]+)>', path)

  def split_arg(arg):
    spl = arg.split(':')
    if len(spl) == 1:
      return {'name': spl[0]}
    else:
      return {'name': spl[1], 'dataType': spl[0]}

  return map(split_arg, args)
