import requests
from flask import Flask, request, abort
from flask_restx import Api, Resource, Namespace, fields

from common import *
from env.kakao import *
from db_connect import FungeDAO
from verify import authenticate_user


db = FungeDAO()
Account = Namespace(name='Account')

@Account.route('/profile')
class User(Resource):
    def get(self):
        id_token = request.headers['Authorization'].split(' ')[1]
        verified = authenticate_user(id_token)
        if not verified: 
            return abort(401, 'Unauthorized')

        response = db.find_one('users', {'id': verified['sub']})
        user = {k: v for k, v in response.items() if k in ['nickname', 'email', 'profile_image_url']}
        return user


@Account.route('/profile/image')
class ProfileImage(Resource):
    def put(self):
        pass

