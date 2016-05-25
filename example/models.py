from flask.ext.restful_swagger_2 import Schema


class EmailModel(Schema):
    type = 'string'
    format = 'email'


class KeysModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string'
        }
    }


class UserModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': EmailModel,
        'keys': KeysModel.array()
    }
    required = ['name']


class ErrorModel(Schema):
    type = 'object'
    properties = {
        'message': {
            'type': 'string'
        }
    }
