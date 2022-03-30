from pathlib import Path

import requests
from flask import Flask, request, abort
from flask_restx import Api, Resource, Namespace, fields

from util import *
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
                return abort(*ERR_NOT_ALLOWED_TYPE(_type))
            if not id_token:
                raise KeyError
        except KeyError:
            return abort(*ERR_TOKEN_NEEDED)
        except IndexError:
            return abort(*ERR_TOKEN_INVALID)

        authed_token = authenticate_user(id_token)
        if not authed_token:
            return abort(*ERR_UNAUTHORIZED)

        verified_token = verify_token(id_token)
        if verified_token == EXPIRED_TOKEN:
            return abort(*ERR_TOKEN_EXPIRED)

        response = db.find_one('users', {'id': verified_token['sub']})
        user = {k: v for k, v in response.items() if k in ['nickname', 'email', 'profile_image_url']}
        return user

    def put(self):
        try:
            _type, id_token = request.headers['Authorization'].split(' ')
            if _type != 'Bearer':
                return abort(*ERR_NOT_ALLOWED_TYPE(_type))
            if not id_token:
                raise KeyError
        except KeyError:
            return abort(*ERR_TOKEN_NEEDED)
        except IndexError:
            return abort(*ERR_TOKEN_INVALID)

        authed_token = authenticate_user(id_token)
        if not authed_token:
            return abort(*ERR_UNAUTHORIZED)

        verified_token = verify_token(id_token)
        if verified_token == EXPIRED_TOKEN:
            return abort(*ERR_TOKEN_EXPIRED)

        uid = verified_token['sub']

        user_info = request.get_json()
        if len(user_info.keys()) != 2:
            return abort(*ERR_NOT_EXPECTED)
        for k in user_info.keys():
            if k not in ['nickname', 'email']:
                return abort(400, 'nickname and email are required.')

        db.find_one_and_update('users', {'id': uid}, {'$set': user_info})
        return {'message': 'Profile has been updated.'}, 201


@Account.route('/profile/image')
class ProfileImage(Resource):
    def post(self):
        try:
            _type, id_token = request.headers['Authorization'].split(' ')
            if _type != 'Bearer':
                return abort(*ERR_NOT_ALLOWED_TYPE(_type))
            if not id_token:
                raise KeyError
        except KeyError:
            return abort(*ERR_TOKEN_NEEDED)
        except IndexError:
            return abort(*ERR_TOKEN_INVALID)

        authed_token = authenticate_user(id_token)
        if not authed_token:
            return abort(*ERR_UNAUTHORIZED)

        verified_token = verify_token(id_token)
        if verified_token == EXPIRED_TOKEN:
            return abort(*ERR_TOKEN_EXPIRED)

        uid = verified_token['sub']

        file = request.files['file']

        path =f"{UPLOAD_PATH}/{UPLOAD_USERS}/{uid}" 
        Path(path).mkdir(parents=True, exist_ok=True)
        extension = file.filename.rsplit('.', 1)[1]

        profile_image_url = upload_file(file, path, 'profile.'+extension)
        if not profile_image_url:
            return {'message': 'Upload failed.'}, 400

        db.find_one_and_update('users', {'id': uid}, {'$set': {'profile_image_url': profile_image_url}})
        return {'message': 'Upload successful.'}, 201
        
