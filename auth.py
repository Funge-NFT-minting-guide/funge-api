import requests
from falsk import Flask
from flask_restx import Api, Resource, Namespace

from common import *
from env.kakao import KKO_REST_KEY

KAKAO_AUTH= 'https://kauth.kakao.com'


Auth = Namespace(name='Auth')

def getKakaoToken(auth):
    parameter = {'grant_type': 'authorization_code', 'client_id': KKO_REST_KEY, 'redirect_uri': f'{SERVICE_URL}:{SERVICE_PORT}', code=auth}
    requests.post(f'{KAKAO_AUTH}/oauth/token', data=parameter)


@Auth.route('/kakao')
class GetAuthorization:
    def get(self):
        pass


