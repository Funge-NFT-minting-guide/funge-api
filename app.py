import logging

from flask_jwt_extended import JWTManager
from flask_restx import Api, Resource
from flask import Flask, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from env.config import *
from common import *
from auth import Auth
from admin import Admin
from account import Account
from minting import Minting


#logging.basicConfig(filename='/var/log/funge-api.log', format='%(message)s', level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ADMIN_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = ADMIN_REFRESH_TOKEN_EXPIRES
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

jwt = JWTManager(app)
api = Api(app=app, version='1.0', title='Funge-API', description="Funge: NFT minting & Guide's API Server")


@app.before_request
def log_request_info():
    data = request.get_data().decode()
    if data:
        logging.info(data)


@api.route('/hello/<string:name>')
class Hello(Resource):
    def get(self, name):
        return {'message': "Welcome, %s!" % name}


@app.route('/uploads/<path:path>')
def user_upload(path):
    return send_from_directory(f'uploads', path)


api.add_namespace(Auth, '/auth')
api.add_namespace(Admin, '/admin')
api.add_namespace(Minting, '/minting')
api.add_namespace(Account, '/account')


if __name__ == '__main__':
    app.run(debug=True, host=SERVICE_HOST, port=SERVICE_PORT)
    print(__name__)
