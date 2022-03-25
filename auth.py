import json
import time
import base64
import datetime
from dateutil.relativedelta import relativedelta

import jwt
import requests
from pymongo import MongoClient
from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, Namespace, reqparse, fields

from common import *
from db_connect import FungeDAO
from env.kakao import *


DAO = FungeDAO()
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


def get_public_key(kid):
    keys = list(DAO.find('kkoPublicKey', {}))
    if not keys:
        keys = requests.get(f'{KAKAO_AUTH}/.well-known/jwks.json').json()['keys']
        keys = [dict(x, **{'expireAt': datetime.datetime.utcnow() + relativedelta(months=+1)}) for x in keys]
        DAO.insert_many('kkoPublicKey', keys)

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
    payload = id_token.split('.')
    decoded_payload = json.loads(base64.b64decode(payload))

    if decoded_payload['iss'] != KAKAO_AUTH:
        return False
    elif decoded_payload['aud'] != KKO_REST_KEY:
        return False
    elif decoded_payload['exp'] < time.time():
        return False
    else:
        return True


@Auth.route('/kakao')
class GetAuthorization(Resource):
    @Auth.marshal_with(id_token)
    def get(self):
        try:
            token = get_kakao_token(request.args['code'])
            if not token or not is_valid_token(token['id_token']):
                return abort(400, 'Token is invalid.')
            if not token or not verify_token(token['id_token']):
                return abort(401, 'Failed to verify your token.')
            else:
                return {'Authorization': f'Bearer {token["id_token"]}'}, 200
        except Exception:
            raise


@Auth.route('/signup')
class Singup(Resource):
    def post(self):
        pass
