import json
import datetime
from dateutil.relativedelta import relativedelta

import jwt
import requests

from common import *
from env.kakao import *
from db_connect import DAO


db = DAO('funge')

def get_public_key(kid):
     keys = list(db.find('kkoPublicKey', {}))
     if not keys:
         keys = requests.get(f'{KAKAO_AUTH}/.well-known/jwks.json').json()['    keys']
         keys = [dict(x, **{'expireAt': datetime.datetime.utcnow() + relativedelta(months=+1)}) for x in keys]
         db.insert_many('kkoPublicKey', keys)

     return list(filter(lambda x: x['kid'] == kid, keys))[0]


def verify_token(id_token, exp=True):
    try:
        decoded_header = jwt.get_unverified_header(id_token)
        public_key = get_public_key(decoded_header['kid'])

        if not public_key:
            return False
        else:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)
            verify_what = {'verify_signature': True, 'verify_aud': True, 'verify_iss': True, 'verify_exp': exp}
            payload = jwt.decode(id_token, key=public_key, algorithms=['RS256'], audience=KKO_REST_KEY, issuer=KAKAO_AUTH, options=verify_what, verify=True)
            return payload
    except jwt.exceptions.ExpiredSignatureError:
        return EXPIRED_TOKEN
    except Exception:
        return INVALID_TOKEN



def get_id_token(uid):
    id_token = db.find_one('idToken', {'id': uid})
    return id_token['id_token'] if id_token else False


def get_auth_id_token(id_token):
    id_token = db.find_one('authIdToken', {'id_token': id_token})
    return id_token['id_token'] if id_token else False
    

def authenticate_user(id_token):
    origin = get_auth_id_token(id_token)
    return origin if origin else False
