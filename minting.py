from flask import Flask
from flask_restx import Api, Resource, Namespace


Minting = Namespace(name='Minting')

@Minting.route('/brief/<string:date>')
class GetMintingBreif(Resource):
    def get(self, date):
        return {'project': 'MetaKongz', 'date': '2022-02-27 10:30', 'mint': '500 KLAY / 5 per 1TX'}
