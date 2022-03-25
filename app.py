from flask import Flask, request
from flask_restx import Api, Resource
from minting import Minting

from common import *


app = Flask(__name__)
api = Api(app=app, version='1.0', title='Funge-API', description="Funge: NFT minting & Guide's API Server")


@api.route('/hello/<string:name>')
class Hello(Resource):
    def get(self, name):
        return {'message': "Welcome, %s!" % name}


api.add_namespace(Minting, '/minting')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=SERVICE_PORT)

