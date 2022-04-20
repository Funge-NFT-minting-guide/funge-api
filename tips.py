import json
import requests

from flask import request, abort
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace, fields, reqparse

from common import *


Tips = Namespace(name='Tips')

parser = reqparse.RequestParser()
parser.add_argument('query', type=str, default={})
parser.add_argument('order', type=int, default=-1, choices=(-1, 1))
parser.add_argument('offset', type=int, default=0)
parser.add_argument('limit', type=int, default=10)
parser.add_argument('flag', type=str, default=None, choices=('invalid', 'outdated', 'processed'))
parser.add_argument('filter', type=str, choices=('_id', 'tweetId'))
parser.add_argument('startdate', type=str)
parser.add_argument('enddate', type=str)

@Tips.route('/faq')
class FAQ(Resource):
    def get(self):
        args = parser.parse_args()
        req_payload = f"{ADMIN_URL}/tips/faq?offset={args['offset']}"
        ret = requests.get(req_payload).json()
        return ret

    def post(self):
        faq = request.get_data()
        req_payload = f'{ADMIN_URL}/tips/faq'
        ret = requests.post(req_payload, faq).json()

        return ret

    def put(self):
        faq = request.get_data()
        req_payload = f'{ADMIN_URL}/tips/faq'
        ret = requests.put(req_payload, faq).json()

        return ret


@Tips.route('/faq/<string:_id>')
class DeleteFAQ(Resource):
    def delete(self, _id):
        req_payload = f'{ADMIN_URL}/tips/faq/{_id}'
        ret = requests.delete(req_payload).json()

        return ret
