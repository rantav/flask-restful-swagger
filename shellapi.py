# Running:
#     python shellapi.py
#

# This is just a test case, not part of the project


__author__ = 'Cosmo Harrigan'


from flask import abort, jsonify
from flask.ext.restful import Resource, reqparse
import socket

COGSERVER_PORT = 17001

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
                   api_spec_url='/api/spec')
###################################


class ShellAPI(Resource):
    """
    Defines a barebones resource for sending shell commands to the CogServer
    """

    # This is because of https://github.com/twilio/flask-restful/issues/134
    @classmethod
    def new(cls, atomspace):
        cls.atomspace = atomspace
        return cls

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('command', type=str, location='args')

        # Setup socket to communicate with OpenCog CogServer
        try:
            self.oc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.oc.connect(('localhost', COGSERVER_PORT))
        except socket.error as msg:
            print msg

        super(ShellAPI, self).__init__()

    def post(self):
        """
        Send a shell command to the cogserver
        Uri: shell

        Include a JSON object with the POST request containing the command
        in a field named "command"

        Examples:

        {'command': 'agents-step'}
        {'command': 'agents-step opencog::SimpleImportanceDiffusionAgent'}
        """

        # Validate, parse and send the command
        data = reqparse.request.get_json()
        if 'command' in data:
            self.oc.send(data['command'])
        else:
            abort(400,
                  'Invalid request: required parameter command is missing')

        return jsonify({'status': 'success'})

api.add_resource(ShellAPI, '/')

if __name__ == '__main__':
  app.run(debug=True)
