'''
Running:

  PYTHONPATH=. python examples/inheritance.py

'''
from flask import Flask
from flask.ext.restful import Api, Resource
from flask_restful_swagger import swagger

app = Flask(__name__, static_folder='../static')

###################################
# This is important:
api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='Inheritance demonstration')
###################################


class Base(Resource):
  def get(self):
    pass

  def post(self):
    pass

  def delete(self):
    pass


class Inherited(Base):
  @swagger.operation(
      notes='just testing inheritance',
      nickname='get',
      parameters=[
          {
            "name": "a_bool",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'boolean',
            "paramType": "path"
          }
      ])
  def get(self):
    return "hello"

  def post(self):
    # wont be visible in the swagger docs
    return "world"

##
## Actually setup the Api resource routing here
##
api.add_resource(Inherited, '/inherited')

if __name__ == '__main__':
  app.run(debug=True)
