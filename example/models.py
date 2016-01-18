from flask.ext.restful_swagger_2 import Schema


class MyModel(Schema):
    type = 'string'
    format = 'email'


class Keys(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string'
        }
    }


class MyOtherModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': MyModel,
        'keys': Keys.array()
    }
    required = ['name']
