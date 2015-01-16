import functools
import inspect
import os
import re

from flask import request, abort, Response
from flask.ext.restful import Resource, fields
from flask_restful_swagger import (
  registry)
from jinja2 import Template

resource_listing_endpoint = None
api_spec_static_suffix = '/_/static/'


def docs(api, apiVersion='0.0', swaggerVersion='1.2',
         basePath='http://localhost:5000',
         resourcePath='/',
         produces=["application/json"],
         api_spec_url='/api/spec',
         description='Auto generated API docs by flask-restful-swagger',
         info={}):
  """
    Main entry point to provide a swagger doc to your REST API.
    optional info dictionary will appear on the swagger html page as a informative header.
    info dict sample is below:
    info = {"title": "Here is the title of the whole API",
        "description": "Here is the general description of the whole API, based on the official swagger.wordnik.com sample.  You can find out more about Swagger \n    at <a href=\"http://swagger.wordnik.com\">http://swagger.wordnik.com</a> or on irc.freenode.net, #swagger.  For this sample,\n    you can use the api key \"special-key\" to test the authorization filters",
        "termsOfServiceUrl": "http://termsOfServiceUrl.example.com",
        "contact": "contact@example.com",
        "license": "MIT",
        "licenseUrl": "http://opensource.org/licenses/MIT"}
  """
  api_add_resource = api.add_resource

  def add_resource(resource, path, *args, **kvargs):
    register_once(api, api_add_resource, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces, api_spec_url, description, info)

    resource = make_class(resource)
    req_registry = _get_current_registry(api=api)

    # Retrieve hierarchy values if this class was annotated with @swagger.resource, else fall back to default one
    hierarchy_id = resource.__dict__.get('__swagger_attr', {}).get('hierarchy_id', 'default')
    hierarchy_description = resource.__dict__.\
      get('__swagger_attr', {}).\
      get('hierarchy_description', 'Operations on {0} resources'.format(hierarchy_id))

    if not hierarchy_id in req_registry['resources_hierarchy'].keys():
      current_hierarchy_endpoint = '{0}/{1}'.format(req_registry['spec_endpoint_path'] , hierarchy_id)
      req_registry['resources_hierarchy'][hierarchy_id] = {
        'link': {
          'path_suffix': current_hierarchy_endpoint,
          'description': hierarchy_description},
        'content': []
      }

      api_add_resource(
        SwaggerRegistry,
        current_hierarchy_endpoint,
        current_hierarchy_endpoint + '.json',
        current_hierarchy_endpoint + '.html',
        endpoint='swaggerregistry/' + hierarchy_id
      )
    #current_hierarchy_endpoint_str.replace('/', '.')
    endpoint = swagger_endpoint(api, resource, path)

    # Add a .help.json help url
    swagger_path = extract_swagger_path(path)

    # Add a .help.html help url
    endpoint_html_str = '{0}/help'.format(swagger_path)
    api_add_resource(
      endpoint,
      "{0}.help.json".format(swagger_path),
      "{0}.help.html".format(swagger_path),
      endpoint=endpoint_html_str)

    return api_add_resource(resource, path, *args, **kvargs)

  api.add_resource = add_resource

  return api

rootPath = os.path.dirname(__file__)


def make_class(class_or_instance):
  if inspect.isclass(class_or_instance):
    return class_or_instance
  return class_or_instance.__class__


def register_once(api, add_resource_func, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces, endpoint_path, description, info):
  global resource_listing_endpoint
  api_spec_static = endpoint_path + api_spec_static_suffix

  if api.blueprint and not registry.get(api.blueprint.name):
    # Most of all this can be taken from the blueprint/app
    registry[api.blueprint.name] = {
      'apiVersion': apiVersion,
      'swaggerVersion': swaggerVersion,
      'basePath': basePath,
      'spec_endpoint_path': endpoint_path,
      'resourcePath': resourcePath,
      'produces': produces,
      'x-api-prefix': '',
      'apis': [],
      'description': description,
      'info': info,
      'resources_hierarchy': {
        'default': {
          'link': {
            # Real 'path' will be rendered at runtime from updated basePath and path_suffix
            'path_suffix': endpoint_path + '/default',
            'description': description
          },
          'content': []
        }
      }
    }

    def registering_blueprint(setup_state):
      reg = registry[setup_state.blueprint.name]
      reg['x-api-prefix'] = setup_state.url_prefix

    api.blueprint.record(registering_blueprint)

    add_resource_func(
      SwaggerRegistry,
      endpoint_path + '/default',
      endpoint_path,
      endpoint_path + '.json',
      endpoint_path + '.html'
    )

    resource_listing_endpoint = endpoint_path + '/_/resource_list.json'
    add_resource_func(ResourceLister, resource_listing_endpoint)

    add_resource_func(
      StaticFiles,
      api_spec_static + '<string:dir1>/<string:dir2>/<string:dir3>',
      api_spec_static + '<string:dir1>/<string:dir2>',
      api_spec_static + '<string:dir1>')
  elif not 'app' in registry:
    registry['app'] = {
      'apiVersion': apiVersion,
      'swaggerVersion': swaggerVersion,
      'basePath': basePath,
      'spec_endpoint_path': endpoint_path,
      'resourcePath': resourcePath,
      'produces': produces,
      'x-api-prefix': api.prefix,
      'description': description,
      'info': info,
      'resources_hierarchy': {
        'default': {
          'link': {
            # Real 'path' will be rendered at runtime from updated basePath and path_suffix
            'path_suffix': endpoint_path + '/default',
            'description': description
          },
          'content': []
        }
      }
    }

    add_resource_func(
      SwaggerRegistry,
      endpoint_path + '/default',
      endpoint_path,
      endpoint_path + '.json',
      endpoint_path + '.html',
      endpoint='app/registry'
    )

    resource_listing_endpoint = endpoint_path + '/_/resource_list.json'
    add_resource_func(
      ResourceLister, resource_listing_endpoint,
      endpoint='app/resourcelister')

    add_resource_func(
      StaticFiles,
      api_spec_static + '<string:dir1>/<string:dir2>/<string:dir3>',
      api_spec_static + '<string:dir1>/<string:dir2>',
      api_spec_static + '<string:dir1>',
      endpoint='app/staticfiles')

templates = {}


def render_endpoint(endpoint):
  return render_page("endpoint.html", endpoint.__dict__)


def render_homepage(resource_list_url):
  conf = {'resource_list_url': resource_list_url}
  return render_page("index.html", conf)


def _get_current_registry(api=None):
  # import ipdb;ipdb.set_trace()
  global registry
  app_name = None
  overrides = {}
  if api:
    app_name = api.blueprint.name if api.blueprint else None
  else:
    app_name = request.blueprint
    overrides = {'basePath': request.url_root.rstrip('/')}

  if not app_name:
    app_name = 'app'

  overrides['models'] = registry.get('models', {})

  reg = registry.setdefault(app_name, {})
  reg.update(overrides)

  reg['basePath'] = reg['basePath'] + reg.get('x-api-prefix', '')

  return reg


def render_page(page, info):
  req_registry = _get_current_registry()
  url = req_registry['basePath']
  if url.endswith('/'):
    url = url.rstrip('/')
  conf = {
    'base_url': url + req_registry['spec_endpoint_path'] + api_spec_static_suffix,
    'full_base_url': url + req_registry['spec_endpoint_path'] + api_spec_static_suffix
  }
  if info is not None:
    conf.update(info)
  global templates
  if page in templates:
    template = templates[page]
  else:
    with open(os.path.join(rootPath, 'static', page), "r") as fs:
      template = Template(fs.read())
      templates[page] = template
  mime = 'text/html'
  if page.endswith('.js'):
    mime = 'text/javascript'
  return Response(template.render(conf), mimetype=mime)


class StaticFiles(Resource):

  def get(self, dir1=None, dir2=None, dir3=None):
    req_registry = _get_current_registry()

    if dir1 is None:
      filePath = "index.html"
    else:
      filePath = dir1
      if dir2 is not None:
        filePath = "%s/%s" % (filePath, dir2)
        if dir3 is not None:
          filePath = "%s/%s" % (filePath, dir3)
    if filePath in [
      "index.html", "o2c.html", "swagger-ui.js",
       "swagger-ui.min.js", "lib/swagger-oauth.js"]:
      conf = {'resource_list_url': req_registry['spec_endpoint_path']}
      return render_page(filePath, conf)
    mime = 'text/plain'
    if filePath.endswith(".gif"):
      mime = 'image/gif'
    elif filePath.endswith(".png"):
      mime = 'image/png'
    elif filePath.endswith(".js"):
      mime = 'text/javascript'
    elif filePath.endswith(".css"):
      mime = 'text/css'
    filePath = os.path.join(rootPath, 'static', filePath)
    if os.path.exists(filePath):
      fs = open(filePath, "rb")
      return Response(fs, mimetype=mime)
    abort(404)


class ResourceLister(Resource):
  def get(self):
    req_registry = _get_current_registry()
    apis = []
    if 'resources_hierarchy' in req_registry and req_registry['resources_hierarchy']:
      apis = [{ 'path': req_registry['basePath'] + item['link']['path_suffix'],
                'description': item['link']['description']
              } for item in req_registry['resources_hierarchy'].values() if 'content' in item and item['content']]

    return {
      "apiVersion": req_registry['apiVersion'],
      "swaggerVersion": req_registry['swaggerVersion'],
      "apis": apis,
      "info": req_registry['info']
    }


def swagger_endpoint(api, resource, path):
  endpoint = SwaggerEndpoint(resource, path)
  req_registry = _get_current_registry(api=api)

  # Retrieve hierarchy values if this class was annotated with @swagger.resource, else fall back to default one
  hierarchy_id = resource.__dict__.get('__swagger_attr', {}).get('hierarchy_id', 'default')

  # Only add this endpoint to the swagger registry for documentation if any swagger decorated operation
  if endpoint.__dict__.get('operations', []):
    req_registry['resources_hierarchy'].\
      setdefault(hierarchy_id, {}).\
      setdefault('content', []).\
      append(endpoint.__dict__)

  class SwaggerResource(Resource):
    def get(self):
      if request.path.endswith('.help.json'):
        return endpoint.__dict__
      if request.path.endswith('.help.html'):
        return render_endpoint(endpoint)
  return SwaggerResource


def _sanitize_doc(comment):
  return comment.replace('\n', '<br/>') if comment else comment


def _parse_doc(obj):
  first_line, other_lines = None, None

  full_doc = inspect.getdoc(obj)
  if full_doc:
    line_feed = full_doc.find('\n')
    if line_feed != -1:
      first_line = _sanitize_doc(full_doc[:line_feed])
      other_lines = _sanitize_doc(full_doc[line_feed+1:])
    else:
      first_line = full_doc

  return first_line, other_lines


class SwaggerEndpoint(object):
  def __init__(self, resource, path):
    self.path = extract_swagger_path(path)
    path_arguments = extract_path_arguments(path)
    self.description, self.notes = _parse_doc(resource)
    self.operations = self.extract_operations(resource, path_arguments)

  @staticmethod
  def extract_operations(resource, path_arguments=[]):
    operations = []
    for method in [m.lower() for m in resource.methods]:
      method_impl = resource.__dict__.get(method, None)
      if method_impl is None:
        for cls in resource.__mro__:
          for item_key in cls.__dict__.keys():
            if item_key == method:
              method_impl = cls.__dict__[item_key]
      op = {
          'method': method,
          'parameters': path_arguments,
          'nickname': 'nickname'
      }

      if '__swagger_attr' in method_impl.__dict__:
        # This method was annotated with @swagger.operation
        decorators = method_impl.__dict__['__swagger_attr']
        for att_name, att_value in list(decorators.items()):
          if isinstance(att_value, (str, int, list)):
            if att_name == 'parameters':
              op['parameters'] = merge_parameter_list(
                op['parameters'], att_value)
            else:
              if att_name in op and att_name is not 'nickname' and op[att_name]:
                att_value = '{0}<br/>{1}'.format(att_value, op[att_name])
              op[att_name] = att_value
          elif isinstance(att_value, object):
            op[att_name] = att_value.__name__
        operations.append(op)

      # Only use method_impl summary/notes if not defined in swagger.operation decorator
      default_summary, default_notes = _parse_doc(method_impl)
      if not 'summary' in op:
          op['summary'] = default_summary
      if not 'notes' in op:
          op['notes'] = default_notes

    return operations


def merge_parameter_list(base, override):
  base = list(base)
  names = [x['name'] for x in base]
  for o in override:
    if o['name'] in names:
      for n, i in enumerate(base):
        if i['name'] == o['name']:
          base[n] = o
    else:
      base.append(o)
  return base


class SwaggerRegistry(Resource):
  def get(self):
    req_registry = _get_current_registry()
    if request.path.endswith('.html'):
      return render_homepage(
        req_registry['basePath'] + req_registry['spec_endpoint_path'] + '/_/resource_list.json')

    hierarchy_id = 'default'
    apis = []
    if request.path.endswith(req_registry['spec_endpoint_path']):
      # Retrieve a unified api operations content
      # Usefull to make a diff easily between a runtime app and a git archived state in your continuous integration
      apis= [hierarchy_item['content'] \
             for hierarchy_id, hierarchy_item in req_registry['resources_hierarchy'].items() \
             if 'content' in hierarchy_item and hierarchy_item['content']
      ]
    else:
      for tmp_hierarchy_id, tmp_hierarchy_item in req_registry['resources_hierarchy'].items():
        if request.path.endswith(req_registry['spec_endpoint_path'] + '/' + tmp_hierarchy_id):
          apis = tmp_hierarchy_item['content']

    if not apis:
      apis = req_registry['resources_hierarchy']['default']['content']

    hierarchy_registry = {
      "apiVersion": req_registry['apiVersion'],
      "swaggerVersion": req_registry['swaggerVersion'],
      "basePath": req_registry['basePath'],
      "resourcePath": '{0}/{1}'.format(req_registry['resourcePath'], hierarchy_id),
      "produces": req_registry['produces'],
      "apis": apis,
      "models": req_registry.get('models', {})
    }
    return hierarchy_registry


def resource(**kwargs):
  """
  This dedorator marks a resource class as a swagger resource so that we can easily
  add and extract attributes from it.
  It saves the decorator's key-values at the class level so we can later
  extract them later when add_resource is invoked.
  """
  def inner(k):
    k.__swagger_attr = kwargs
    return k
  return inner


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


def model(c=None, *args, **kwargs):
  add_model(c)
  return c


class _Nested(object):
  def __init__(self, klass, **kwargs):
    self._nested = kwargs
    self._klass = klass

  def __call__(self, *args, **kwargs):
    return self._klass(*args, **kwargs)

  def nested(self):
    return self._nested


# wrap _Cache to allow for deferred calling
def nested(klass=None, **kwargs):
  if klass:
    ret = _Nested(klass)
    functools.update_wrapper(ret, klass)
  else:
    def wrapper(klass):
      wrapped = _Nested(klass, **kwargs)
      functools.update_wrapper(wrapped, klass)
      return wrapped
    ret = wrapper
  return ret


def add_model(model_class):
  models = registry['models']
  name = model_class.__name__
  model = models[name] = {'id': name}
  model['description'], model['notes'] = _parse_doc(model_class)
  if 'resource_fields' in dir(model_class):
    # We take special care when the model class has a field resource_fields.
    # By convension this field specifies what flask-restful would return when
    # this model is used as a return value from an HTTP endpoint.
    # We look at the class and search for an attribute named
    # resource_fields.
    # If that attribute exists then we deduce the swagger model by the content
    # of this attribute

    if hasattr(model_class, 'required'):
      required = model['required'] = model_class.required

    properties = model['properties'] = {}
    nested = model_class.nested() if isinstance(model_class, _Nested) else {}
    for field_name, field_type in list(model_class.resource_fields.items()):
      nested_type = nested[field_name] if field_name in nested else None
      properties[field_name] = deduce_swagger_type(field_type, nested_type)
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
      defaults = list(
        zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
    properties = model['properties'] = {}
    required_args_count = len(argspec.args) - len(defaults)
    for arg in argspec.args[:required_args_count]:
      required.append(arg)
      # type: string for lack of better knowledge, until we add more metadata
      properties[arg] = {'type': 'string'}
    for k, v in defaults:
      properties[k] = {'type': 'string', "default": v}

  if 'swagger_metadata' in dir(model_class):
    for field_name, field_metadata in model_class.swagger_metadata.items():
        if field_name in properties:
            properties[field_name].update(field_metadata)

def deduce_swagger_type(python_type_or_object, nested_type=None):
    import inspect

    if inspect.isclass(python_type_or_object):
        predicate = issubclass
    else:
        predicate = isinstance
    if predicate(python_type_or_object, (str,
                                         fields.String,
                                         fields.FormattedString,
                                         fields.Url,
                                         int,
                                         fields.Integer,
                                         float,
                                         fields.Float,
                                         fields.Arbitrary,
                                         fields.Fixed,
                                         bool,
                                         fields.Boolean,
                                         fields.DateTime)):
        return {'type': deduce_swagger_type_flat(python_type_or_object)}
    if predicate(python_type_or_object, (fields.List)):
        if inspect.isclass(python_type_or_object):
          return {'type': 'array'}
        else:
          return {'type': 'array',
                  'items': {
                    '$ref': deduce_swagger_type_flat(
                      python_type_or_object.container, nested_type)}}
    if predicate(python_type_or_object, (fields.Nested)):
        return {'type': nested_type}

    return {'type': 'null'}


def deduce_swagger_type_flat(python_type_or_object, nested_type=None):
    if nested_type:
      return nested_type
    import inspect

    if inspect.isclass(python_type_or_object):
        predicate = issubclass
    else:
        predicate = isinstance
    if predicate(python_type_or_object, (str,
                                         fields.String,
                                         fields.FormattedString,
                                         fields.Url)):
        return 'string'
    if predicate(python_type_or_object, (int,
                                         fields.Integer)):
        return 'integer'
    if predicate(python_type_or_object, (float,
                                         fields.Float,
                                         fields.Arbitrary,
                                         fields.Fixed)):
        return 'number'
    if predicate(python_type_or_object, (bool,
                                         fields.Boolean)):
        return 'boolean'
    if predicate(python_type_or_object, (fields.DateTime,)):
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
      return {'name': spl[0],
              'dataType': 'string',
              'paramType': 'path'}
    else:
      return {'name': spl[1],
              'dataType': spl[0],
              'paramType': 'path'}

  return list(map(split_arg, args))
