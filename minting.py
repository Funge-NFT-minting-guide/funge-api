import json
import requests

from flask import request, abort
from flask_restx import Resource, Namespace, fields, reqparse

from common import *


Minting = Namespace(name='Minting')

minting_tweet = Minting.model('MintingTweet', {
    '_id': fields.String(readonly=True),
    'id': fields.String(readonly=True),
    'created_at': fields.DateTime(),
    'text': fields.String(),
    'user': fields.String(),
    'uid': fields.String(),
    'profile_image_url': fields.String(),
    'followers': fields.Integer(),
    'url': fields.String(),
    'invalid': fields.Boolean(),
    'outdated': fields.Boolean(),
    'processed': fields.Boolean()
    })

minting_info_detail = Minting.model('MintingInfoDetail', {
    'mintingType': fields.String,
    'mintingTime': fields.DateTime,
    'mintingPrice': fields.Integer,
    'mintingCurrency': fields.String,
    'mintingAmount': fields.String
    })

minting_info = Minting.model('MintingInfo', {
    '_id': fields.String(readonly=True),
    'tweetId': fields.String(readonly=True),
    'profileImageUrl': fields.String(),
    'followers': fields.Integer(),
    'url': fields.String(),
    'projectName': fields.String(),
    'date': fields.Date(),
    'site': fields.String(),
    'etc': fields.String(),
    })


parser = reqparse.RequestParser()
parser.add_argument('query', type=str, default={})
parser.add_argument('order', type=int, default=-1, choices=(-1, 1))
parser.add_argument('offset', type=int, default=0)
parser.add_argument('limit', type=int, default=10)
parser.add_argument('flag', type=str, default=None, choices=('invalid', 'outdated', 'processed'))
parser.add_argument('filter', type=str, choices=('_id', 'tweetId'))
parser.add_argument('startdate', type=str)
parser.add_argument('enddate', type=str)


@Minting.route('/tweets')
class MintingTweets(Resource):
    @Minting.marshal_list_with(minting_tweet)
    def get(self):
        args = parser.parse_args()
        req_payload = f"{TWITTY_URL}/minting/tweets?query={args['query']}&order={args['order']}&offset={args['offset']}&limit={args['limit']}"
        ret = requests.get(req_payload).json()
        return ret


@Minting.route('/tweets/<string:tid>')
class MintingTweetsOne(Resource):
    @Minting.marshal_with(minting_tweet)
    def get(self, tid):
        req_payload = f"{TWITTY_URL}/minting/tweets/{tid}"
        ret = requests.get(req_payload).json()
        return [ret] if ret else abort(*ERR_NOT_FOUND)


    def put(self, tid):
        args = parser.parse_args()
        req_payload = f"{TWITTY_URL}/minting/tweets/{tid}?flag={args['flag']}"
        ret = requests.put(req_payload).json()
        return [ret] if ret else abort(*ERR_NOT_FOUND)


@Minting.route('/tweets/total')
class MintingTweetsTotal(Resource):
    def get(self):
        req_payload = f"{TWITTY_URL}/minting/tweets/total"
        ret = requests.get(req_payload).json()
        return ret


@Minting.route('/data/total')
class MintingDataTotal(Resource):
    def get(self):
        args = parser.parse_args()
        req_payload = f"{TWITTY_URL}/minting/data/total?query={args['query']}"
        ret = requests.get(req_payload).json()
        return ret
        


@Minting.route('/info')
class MintingInfo(Resource):
    @Minting.marshal_list_with(minting_info)
    def get(self):
        req_payload = f"{ADMIN_URL}/minting/info"
        ret = requests.get(req_payload).json()
        return ret


    def post(self):
        req_payload = f"{ADMIN_URL}/minting/info"
        ret = requests.post(req_payload, data=request.data).json()
        return ret


@Minting.route('/info/<string:tweet_id>')
class MintingInfoTid(Resource):
    def get(self, tweet_id):
        args = parser.parse_args()
        req_payload = f"{ADMIN_URL}/minting/info/{tweet_id}?filter={args['filter']}"
        ret = requests.get(req_payload)
        print(ret.json())
        return ret.json() if ret.status_code == 200 else abort(*ERR_NOT_FOUND)


@Minting.route('/info/total')
class MintingInfoTotal(Resource):
    def get(self):
        req_payload = f"{ADMIN_URL}/minting/info/total"
        ret = requests.get(req_payload).json()
        return ret


@Minting.route('/info/total/date')
class MintingInfoTotalDate(Resource):
    def get(self):
        args = parser.parse_args()
        req_payload = f"{ADMIN_URL}/minting/info/total/date?startdate={args['startdate']}&enddate={args['enddate']}"
        ret = requests.get(req_payload).json()
        return ret
















