from flask.ext.restful import Resource
import inspect
import functools
import re
import flask_restful
from flask_restful_swagger import registry, registered


def docs(api, apiVersion='0.0', swaggerVersion='1.2',
         basePath='http://localhost:5000',
         resourcePath='/',
         produces=["application/json"],
         api_spec_url='/api/spec.json'):

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
                  resourcePath, produces, api_spec_url)
    return api_add_resource(resource, path, *args, **kvargs)
  api.add_resource = add_resource

  return api


def register_once(add_resource, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces, api_spec_url):
  global registered
  if not registered:
    registered = True
    registry['apiVersion'] = apiVersion
    registry['swaggerVersion'] = swaggerVersion
    registry['basePath'] = basePath
    registry['resourcePath'] = resourcePath
    registry['produces'] = produces
    add_resource(SwaggerRegistry, api_spec_url)


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
    self.description = inspect.getdoc(resource)
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
      op['summary'] = inspect.getdoc(method_impl)
      if '__swagger_attr' in method_impl.__dict__:
        # This method was annotated with @swagger.operation
        decorators = method_impl.__dict__['__swagger_attr']
        for att_name, att_value in decorators.items():
          if isinstance(att_value, (basestring, int, list)):
            op[att_name] = att_value
          elif isinstance(att_value, object):
            op[att_name] = att_value.__name__
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
  add_model(c)
  return inner


def add_model(model_class):
  models = registry['models']
  name = model_class.__name__
  model = models[name] = {'id': name}
  model['description'] = inspect.getdoc(model_class)
  if 'resource_fields' in dir(model_class):
    # We take special care when the model class has a field resource_fields.
    # By convension this field specifies what flask-restful would return when
    # this model is used as a return value from an HTTP endpoint.
    # We look at the class and search for an attribute named
    # resource_fields.
    # If that attribute exists then we deduce the swagger model by the content
    # of this attribute
    properties = model['properties'] = {}
    for field_name, field_type in model_class.resource_fields.iteritems():
      properties[field_name] = {'type': deduce_swagger_type(field_type)}
  elif '__init__' in dir(model_class):
    # Alternatively, if a resource_fields does not exist, we deduce the model
    # fields from the parameters sent to its __init__ method

    # Credits for this snippet go to Robin Walsh
    # https://github.com/hobbeswalsh/flask-sillywalk
    argspec = inspect.getargspec(model_class.__init__)
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


def deduce_swagger_type(python_type):
  if issubclass(python_type, (basestring,
                              flask_restful.fields.String,
                              flask_restful.fields.FormattedString,
                              flask_restful.fields.Url)):
    return 'string'
  if issubclass(python_type, (int,
                              flask_restful.fields.Integer)):
    return 'integer'
  if issubclass(python_type, (float,
                              flask_restful.fields.Float,
                              flask_restful.fields.Arbitrary,
                              flask_restful.fields.Fixed)):
    return 'number'
  if issubclass(python_type, (bool,
                              flask_restful.fields.Boolean)):
    return 'boolean'
  if issubclass(python_type, (flask_restful.fields.DateTime)):
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
