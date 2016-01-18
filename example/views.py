from models import MyOtherModel
from flask.ext.restful_swagger_2 import swagger, Resource


class Hello(Resource):
    @swagger.doc({
        'tags': ['Foo'],
        'description': 'Dat description',
        'summary': 'upload',
        'parameters': [
            {
                'name': 'bang',
                'description': 'Moar description',
                'in': 'query',
                'type': 'string',
            }
        ],
        'responses': {
            '200': {
                'description': 'supergeil',
                'schema': MyOtherModel
            }
        }
    })
    def get(self):
        return MyOtherModel(name='hi')


class SomeParams(Resource):
   @swagger.doc({
       'tags': ['Foo', 'Fa'],
       'description': 'I take a path param',
       'parameters': [
           {
               'name': 'value',
               'description': 'I will double that',
               'in': 'path',
               'type': 'int'
           }
       ],
       'responses': {
           '200': {
               'description': 'So integer',
               'schema': {
                   'type': 'integer'
               }
           }
       }
   })
   def get(self, value):
       return value * 2