from flask import after_this_request
from flask import request, make_response

from flask_restful import Resource
from flask_pydantic import validate
from flask_jwt_extended import jwt_required

from common.security import authenticate
from common.security import expire_token
from common.security import refresh_expiration

from schemas.auth import AuthSchema


class Login(Resource):
    @validate()
    def post(self, body: AuthSchema):
        try:
            response = authenticate(body.identifier, body.password)
        except ValueError as e:
            response = make_response({"msg": str(e)}, 400)
            response = expire_token(response)
            return response
        else:
            return response


class Logout(Resource):
    @jwt_required()
    def post(self):
        try:
            response = {"msg": "Successfully logged out."}
            response = make_response(response, 200)
            response = expire_token(response)
        except Exception as e:
            response = {"msg": str(e)}
            response = make_response(response, 400)
            return response
        else:
            return response


# @jwt_required()
# def get(self):
#    response = {"msg": "success"}
#    response = make_response(response, 200)
#    @after_this_request
#    def after_request(response):
#        response = refresh_expiration(response)
#        return response
#    return response
