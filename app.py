import logging
from flask import Flask, request
from flask_restx import Api, Resource

from common import *
from auth import Auth
from account import Account
from minting import Minting


logging.basicConfig(filename='/var/log/funge-api.log', format='[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] - %(message)s', level=logging.DEBUG)


app = Flask(__name__)
api = Api(app=app, version='1.0', title='Funge-API', description="Funge: NFT minting & Guide's API Server")


@api.route('/hello/<string:name>')
class Hello(Resource):
    def get(self, name):
        return {'message': "Welcome, %s!" % name}


api.add_namespace(Minting, '/minting')
api.add_namespace(Auth, '/auth')
api.add_namespace(Account, '/account')


if __name__ == '__main__':
    app.run(debug=True, host=SERVICE_HOST, port=SERVICE_PORT)

