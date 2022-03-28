import json
import time
import base64
import pprint
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

import jwt
import requests

from common import *
from env.kakao import *
from db_connect import FungeDAO


db = FungeDAO()

def get_public_key(kid):
     keys = list(db.find('kkoPublicKey', {}))
     if not keys:
         keys = requests.get(f'{KAKAO_AUTH}/.well-known/jwks.json').json()['    keys']
         keys = [dict(x, **{'expireAt': datetime.datetime.utcnow() + relativedelta(months=+1)}) for x in keys]
         db.insert_many('kkoPublicKey', keys)

     return list(filter(lambda x: x['kid'] == kid, keys))[0]


def verify_token(token):
    payload = False
    try:
        decoded_header = jwt.get_unverified_header(token)
        public_key = get_public_key(decoded_header['kid'])

        if not public_key:
            return False
        else:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)
            options = {"verify_signature": True, "verify_aud": False, "verify_exp": False}
            payload = jwt.decode(token, key=public_key, algorithms=['RS256'], options=options)
            print(payload)
            return payload
    except Exception:
        raise
    finally:
        return payload


def get_id_token(uid):
    id_token = db.find_one('idToken', {'id': uid})
    return id_token['id_token'] if id_token else False
    

def authenticate_user(id_token):
    verified_token = verify_token(id_token)
    if not verified_token:
        return False
    if id_token == get_id_token(verified_token['sub']):
        return verified_token
