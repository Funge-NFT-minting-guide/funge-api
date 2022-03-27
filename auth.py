import json
import time
import base64
import datetime
from dateutil.relativedelta import relativedelta

import jwt
import requests
from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, Namespace, reqparse, fields

from common import *
from env.kakao import *
from db_connect import FungeDAO


db = FungeDAO()
Auth = Namespace(name='Auth')

id_token = Auth.model('ID_TOKEN', {'Authorization': fields.String()})

def get_kakao_token(auth):
    parameter = {'grant_type': 'authorization_code', 'client_id': KKO_REST_KEY, 'redirect_uri': f'{SERVICE_URL}:{SERVICE_PORT}/auth/kakao', 'code': auth}
    response = requests.post(f'{KAKAO_AUTH}/oauth/token', data=parameter).json()
    print(response)
    if 'access_token' in response:
        return response
    else:
        print(response)
        return False


def get_public_key(kid):
    keys = list(db.find('kkoPublicKey', {}))
    if not keys:
        keys = requests.get(f'{KAKAO_AUTH}/.well-known/jwks.json').json()['keys']
        keys = [dict(x, **{'expireAt': datetime.datetime.utcnow() + relativedelta(months=+1)}) for x in keys]
        db.insert_many('kkoPublicKey', keys)

    return list(filter(lambda x: x['kid'] == kid, keys))[0]


def verify_token(token):
    decoded_header = jwt.get_unverified_header(token)
    public_key = get_public_key(decoded_header['kid'])

    if not public_key:
        return False
    else:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)
        try:
            options = {"verify_signature": True, "verify_aud": False}
            payload = jwt.decode(token, key=public_key, algorithms=['RS256'], options=options)
            print(payload)
            return payload
        except Exception:
            raise

def is_valid_token(id_token):
    payload = id_token.split('.')[1]
    decoded_payload = json.loads(base64.b64decode(payload))

    if decoded_payload['iss'] != KAKAO_AUTH:
        return False
    elif decoded_payload['aud'] != KKO_REST_KEY:
        return False
    elif decoded_payload['exp'] < time.time():
        return False
    else:
        return True


def set_access_token(uid, access_token):
    db.find_one_and_update('accessToken', {'id': uid}, {'$set': {'id': uid, 'access_token': access_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)


def get_access_token(uid):
    access_token = db.find_one('accessToken', {'id': uid})
    if not access_token:
        access_token = refresh_access_token(uid)
        set_access_token(uid, access_token)
    return access_token


def set_refresh_token(uid, refresh_token):
    db.find_one_and_update('refreshToken', {'id': uid}, {'$set': {'id': uid, 'refresh_token': refresh_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)


def get_refresh_token(uid):
    refresh_token = db.find_one('refreshToken', {'id': uid})
    return refresh_token if refresh_token else False


def refresh_access_token(uid):
    refresh_token = get_refresh_token(uid)
    if not refresh_token:
        False

    parameter = {'grant_type': 'refresh_token', 'client_id': KKO_REST_KEY, 'refresh_token': refresh_token}
    response = requests.post(f'{KAKAO_AUTH}/oauth/token', data=parameter).json()
    print(response)
    
    set_access_token(uid, response['access_token'])
    if 'refresh_token' in response.keys():
        set_refresh_token(uid, response['refresh_token'])


def set_id_token(uid, id_token):
    db.find_one_and_update('idToken', {'id': uid}, {'$set': {'id': uid, 'id_token': id_token, 'createdAt': datetime.datetime.utcnow()}}, upsert=True)



def signup(id_token):
    pass


@Auth.route('/kakao')
class GetAuthorization(Resource):
    @Auth.marshal_with(id_token)
    def get(self):
        try:
            token = get_kakao_token(request.args['code'])
            id_token = verify_token(token['id_token'])
            if not token:
                return abort(400, 'Token is not issued.')
            elif not is_valid_token(token['id_token']):
                return abort(400, 'Token is invalid.')
            elif not id_token:
                return abort(401, 'Failed to verify your token.')
            else:
                set_access_token(id_token['sub'], token['access_token'])
                set_refresh_token(id_token['sub'], token['refresh_token'])
                signup(id_token)
                return {'Authorization': f'Bearer {token["id_token"]}'}, 200
        except Exception:
            raise

