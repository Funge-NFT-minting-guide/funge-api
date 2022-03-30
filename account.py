import requests
from flask import Flask, request, abort
from flask_restx import Api, Resource, Namespace, fields

from common import *
from env.kakao import *
from db_connect import FungeDAO
from verify import verify_token, authenticate_user


db = FungeDAO()
Account = Namespace(name='Account')

@Account.route('/profile')
class User(Resource):
    def get(self):
        try:
            _type, id_token = request.headers['Authorization'].split(' ')
            if _type != 'Bearer':
                return abort(400, f'{_type} type is not allowed.')
            if not id_token:
                raise KeyError
        except KeyError:
            return abort(400, 'Token is needed.')
        except IndexError:
            return abort(400, 'Token is not valid.')

        authed_token = authenticate_user(id_token)
        if not authed_token:
            return abort(401, 'Unauthorized')

        verified_token = verify_token(id_token)

        response = db.find_one('users', {'id': verified_token['sub']})
        user = {k: v for k, v in response.items() if k in ['nickname', 'email', 'profile_image_url']}
        return user


@Account.route('/profile/image')
class ProfileImage(Resource):
    def put(self):
        pass

