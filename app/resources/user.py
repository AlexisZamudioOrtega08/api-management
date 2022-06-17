from flask import make_response
from flask_pydantic import validate
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required

from schemas.user import UserSchema, UpdateUserSchema
from models.user import User as UserModel

from common.util import UserHelper
from common.util import filter, is_admin
from common.security import expire_token


class User(Resource):
    def __init__(self):
        self.message = {"user": "fail", "billing": "fail"}

    @jwt_required()
    @validate()
    def put(self, body: UpdateUserSchema):
        try:
            user = None
            if is_admin() and body.identifier == None:
                raise ValueError("You must provide an identifier.")
            is_duplicate, desription = UserHelper.find_duplicate(body=body)
            if is_duplicate:
                raise ValueError(desription)
            if body.username != None:
                raise ValueError("You can't change username.")
            user, flag, expire = UserHelper.update_body(body)
            if not flag:
                return {"msg": "No changes detected."}, 200
            else:
                user.save_to_db()
        except (Exception, ValueError) as e:
            if user:
                user.rollback()
            if e.__class__.__name__ == "ValueError":
                if e.args[0] == "Forbidden.":
                    return {"msg": "You are not authorized to change role"}, 403
                return {"msg": str(e)}, 400
            elif e.__class__.__name__ == "IntegrityError":
                return {"msg": str(e)}, 400
        else:
            if user:
                user.commit()
            response = make_response({"msg": "User updated successfully!"}, 200)
            if expire:
                response = expire_token(response)
            return response

    @validate()
    def post(self, body: UserSchema):
        try:
            is_duplicate, description = UserHelper.find_duplicate(body)
            if is_duplicate:
                return {"message": str(description)}, 400
            else:
                user = UserModel(**body.dict())
                user.save_to_db()
        except:
            user.rollback()
            return {"message": "an error occurred creating the user."}, 500
        else:
            user_id = user.commit(id=True)
            return UserHelper.post_billing(self.message, user_id)

    @jwt_required()
    def delete(self):
        try:
            if not is_admin():
                return {"msg": "Forbidden"}, 403
            id = request.args.get("id", default=0, type=int)
            if id == 0:
                return {"message": "id is required"}, 400
            user = UserModel.find_by(id=id)
            if user:
                user.delete_from_db()
            else:
                return {"message": "user not found"}, 404
        except Exception as e:
            if user:
                user.rollback()
            return {"message": "An error occurred deleting the user."}, 500
        else:
            if user:
                user.commit()
            return {"message": "user deleted successfully!"}, 200


class FilterUser(Resource):
    @jwt_required()
    @validate()
    def get(self, filter_by: str):
        try:
            if not is_admin():
                return {"msg": "Forbidden"}, 403
            page = request.args.get("page", default=1, type=int)
            limit = request.args.get("limit", default=10, type=int)
            value = request.args.get("value", default=None, type=str)
            if value is None and filter_by != "all":
                return {"msg": "param: {value} is required"}, 400
            offset = (page - 1) * limit
            users, pages = filter("user", value, offset, limit, filter_by)
        except (ValueError, Exception) as e:
            if e.__class__.__name__ == "ValueError":
                return {"msg": str(e)}, 400
            else:
                return {"msg": str(e)}, 500
        else:
            return (
                {"users": [user.json() for user in users], "pages": str(pages),},
                200,
                {"Content-Type": "application/json"},
            )
