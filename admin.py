import re
import json
import time
import string
import base64
import binascii
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

import bcrypt
import requests
from flask import Flask, request, jsonify, abort, make_response
from flask_restx import Api, Resource, Namespace, reqparse, fields
from flask_jwt_extended import (jwt_required, create_access_token, get_jwt_identity, set_access_cookies)

from common import *
from env.kakao import *
from db_connect import DAO
from verify import verify_token, authenticate_user


db = DAO('funge')
Admin = Namespace(name='Admin')

username_allowed = string.ascii_letters + string.digits + '_-'
password_allowed = username_allowed + '$@$!%*#?&'

is_allowed = lambda x, y: all([c in y for c in list(x)])

def validate_username(username):
    if not username or len(username) < 4:
        return False
    elif not is_allowed(username, username_allowed):
        return False
    else:
        return True


def validate_password(password):
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&_-])[A-Za-z\d$@$!%*#?&_-]{9,}$', password):
        return False
    else:
        return True



@Admin.route('/signup')
class Signup(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if not validate_username(username) or not validate_password(password):
            abort(400, 'username or password is invalid.')

        if db.find_one('admin', {'username': username}):
            abort(409, 'User already exists.')
        
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db.insert_one('admin', {'username': username, 'password': password_hash})


@Admin.route('/signin')
class Signin(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        
        if not username or not password:
            abort(400, 'username or password is incorrect.')

        user = db.find_one('admin', {'username': username})
        if not user:
            abort(400, 'username or password is incorrect.')

        if bcrypt.checkpw(password.encode(), user['password']):
            access_token = create_access_token(identity=user['username'])
            response = jsonify({'msg': 'Login successful.'})
            set_access_cookies(response, access_token)
            response.set_cookie('isAuthenticated', 'true')
            print(response)
            return response
        else:
            abort(400, 'username or password is incorrect.')


@Admin.route('/signout')
class Signout(Resource):
    @jwt_required()
    def get(self):
        response = make_response()
        response.delete_cookie('access_token_cookie')
        response.delete_cookie('isAuthenticated')
        return response



@Admin.route('/protected')
class Protected(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'msg': f'authenticated for {current_user}.'}
