import json
import time
import base64
import pprint
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

import requests
from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, Namespace, reqparse, fields

from common import *
from env.kakao import *
from db_connect import FungeDAO
from verify import verify_token

db = FungeDAO()
Auth = Namespace(name='Auth')

id_token = Auth.model('ID_TOKEN', {'Authorization': fields.String()})

def get_kakao_token(auth):
    parameter = {'grant_type': 'authorization_code', 'client_id': KKO_REST_KEY, 'redirect_uri': f'{SERVICE_URL}:{SERVICE_PORT}/auth/kakao', 'code': auth}
    response = requests.post(f'{KAKAO_AUTH}/oauth/token', data=parameter).json()
    if 'access_token' in response:
        return response
    else:
        print(response)
        return False


def is_valid_token(id_token):
    payload = id_token.split('.')[1]
    decoded_payload = json.loads(base64.b64decode(payload))

    if decoded_payload['iss'] != KAKAO_AUTH:
        return False
    elif decoded_payload['aud'] != KKO_REST_KEY:
        return False
    elif decoded_payload['exp'] < time.time():
        return ERR_EXP, decoded_payload
    else:
        return SUCCESS, decoded_payload


def set_access_token(uid, access_token):
    db.find_one_and_update('accessToken', {'id': uid}, {'$set': {'id': uid, 'access_token': access_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)


def get_access_token(uid):
    access_token = db.find_one('accessToken', {'id': uid})
    return access_token['access_token'] if access_token else False


def set_refresh_token(uid, refresh_token):
    db.find_one_and_update('refreshToken', {'id': uid}, {'$set': {'id': uid, 'refresh_token': refresh_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)


def get_refresh_token(uid):
    refresh_token = db.find_one('refreshToken', {'id': uid})
    return refresh_token['refresh_token'] if refresh_token else False


def set_id_token(uid, id_token):
    db.find_one_and_update('idToken', {'id': uid}, {'$set': {'id': uid, 'id_token': id_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)


def get_id_token(uid):
    id_token = db.find_one('idToken', {'id': uid})
    return id_token['id_token'] if id_token else False


def refresh_access_token(uid):
    refresh_token = get_refresh_token(uid)
    if not refresh_token:
        False

    parameter = {'grant_type': 'refresh_token', 'client_id': KKO_REST_KEY, 'refresh_token': refresh_token}
    response = requests.post(f'{KAKAO_AUTH}/oauth/token', data=parameter).json()
    print(response)
    access_token = response['access_token']
    id_token = response['id_token']
    
    set_access_token(uid, access_token)
    set_id_token(uid, id_token)
    if 'refresh_token' in response.keys():
        set_refresh_token(uid, response['refresh_token'])


def refresh_id_token(uid):
    refresh_access_token(uid)
    id_token = get_id_token(uid)

    return id_token if id_token else False

def get_kakao_user(uid):
    access_token = get_access_token(uid)
    header = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(f'{KAKAO_API}/v2/user/me', headers=header).json()

    user_info = dict()
    user_info['id'] = uid
    user_info['connected_at'] = dateutil.parser.isoparse(response['connected_at'])
    user_info['nickname'] = response['properties']['nickname']
    user_info['email'] = response['kakao_account']['email']
    if response['kakao_account']['has_age_range']:
        user_info['age_range'] = response['kakao_account']['age_range']
    if response['kakao_account']['has_birthday']:
        user_info['birthday'] = response['kakao_account']['birthday']
    if response['kakao_account']['has_gender']:
        user_info['gender'] = response['kakao_account']['gender']

    return user_info
    

def set_user_info(uid, user_info):
    db.find_one_and_update('users', {'id': uid}, {'$set': user_info}, upsert=True)
    

def signup(uid, id_token):
    set_id_token(uid, id_token)
    user_info = get_kakao_user(uid)
    set_user_info(uid, user_info)


@Auth.route('/kakao')
class GetAuthorization(Resource):
    @Auth.marshal_with(id_token)
    def get(self):
        try:
            token = get_kakao_token(request.args['code'])
            verified_token = verify_token(token['id_token'])
            if not token:
                return abort(400, 'Token is not issued.')
            elif not is_valid_token(token['id_token']):
                return abort(400, 'Token is invalid.')
            elif not verified_token:
                return abort(401, 'Failed to verify your token.')
            else:
                uid = verified_token['sub']
                set_access_token(uid, token['access_token'])
                set_refresh_token(uid, token['refresh_token'])
                signup(uid, token['id_token'])
                return {'Authorization': f'Bearer {token["id_token"]}'}, 200
        except Exception:
            raise


@Auth.route('/login')
class Login(Resource):
    def get(self):
        id_token = request.headers['Authorization'].split(' ')[1]
        is_valid, payload = is_valid_token(id_token)
        if not id_token:
            return abort(400, 'Token is needed.')
        elif not is_valid:
            return abort(400, 'Token is invalid.')
        elif is_valid == ERR_EXP:
            id_token = refresh_id_token(payload['sub'])
        else:
            if verify_token(id_token):
                return {'Authorization': f'Bearer {id_token}'}, 200
            else:
                return abort(400, 'Token is invalid')
