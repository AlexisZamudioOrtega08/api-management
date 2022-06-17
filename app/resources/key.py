import secrets

from flask_jwt_extended import jwt_required
from flask_restful import Resource, request

from models.key import Key as KeyModel
from models.user import User as UserModel

from flask_pydantic import validate
from schemas.key import KeySchema

from common.util import is_admin
from common.util import filter


class Key(Resource):
    @validate()
    def post(self, body: KeySchema):
        try:
            record = None
            key = secrets.token_urlsafe(30)
            user = UserModel.find_by(id=body.user_id)
            if not user:
                raise ValueError("User not found.")
            record = KeyModel(key=key, user_id=body.user_id)
            if record:
                record.save_to_db()
        except (Exception, ValueError) as e:
            if record:
                record.rollback
            if e.__class__.__name__ == "ValueError":
                if e.args[0] == "User not found.":
                    return {"msg": "User not found."}, 404
            if e.__class__.__name__ == "IntegrityError":
                return {"msg": str(e)}, 400
            else:
                return {"msg": str(e)}, 500
        else:
            key = record.key
            record.commit()
            return {"msg": "key added successfully!", "key": str(key)}, 201

    @jwt_required()
    def delete(self, id: int):
        try:
            id = request.args.get("id", default=0, type=int)
            if id == 0:
                return {"message": "id is required"}, 400
            record = KeyModel.find_by(id=id)
            if record:
                record.delete_from_db()
            else:
                return {"message": "Key not found"}, 404
        except Exception as e:
            if record:
                record.rollback()
            return {"message": "An error occurred deleting the key."}, 500
        else:
            if record:
                record.commit()
            return {"message": "key deleted successfully!"}, 200


class FilterKey(Resource):
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
            users, pages = filter("key", value, offset, limit, filter_by)
        except (ValueError, Exception) as e:
            if e.__class__.__name__ == "ValueError":
                return {"msg": str(e)}, 400
            else:
                return {"msg": str(e)}, 500
        else:
            return (
                {"keys": [user.json() for user in users], "pages": str(pages),},
                200,
                {"Content-Type": "application/json"},
            )
