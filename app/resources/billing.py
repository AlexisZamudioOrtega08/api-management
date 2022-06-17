from flask_restful import Resource, request
from flask_pydantic import validate

from models.billing import Billing as BillingModel
from schemas.billing import BillingSchema
from common.util import filter, is_admin

from flask_jwt_extended import jwt_required


class Billing(Resource):
    @jwt_required()
    @validate()
    def post(self, body: BillingSchema):
        try:
            bill = BillingModel.find_by(user_id=body.user_id)
            if bill:
                return {"msg": "A billing linked to user already exist."}, 400
            bill = BillingModel(**body.dict())
            bill.save_to_db()
        except Exception as e:
            return {"msg": str(e)}, 500
        else:
            bill.commit()
            return {"msg": "billing created successfully!"}, 200

    @jwt_required()
    @validate()
    def put(self, body: BillingSchema):
        try:
            bill = None
            if not is_admin():
                raise ValueError("Forbidden.")
            bill = BillingModel.find_by(user_id=body.user_id)
            if bill:
                bill.balance = body.balance + bill.balance
                bill.save_to_db()
            else:
                raise ValueError("User not found.")
        except (Exception, ValueError) as e:
            if bill:
                bill.rollback()
            if e.__class__.__name__ == "ValueError":
                if e.args[0] == "Forbidden.":
                    return {"msg": "Forbidden."}, 403
                return {"msg": str(e)}, 400
            elif e.__class__.__name__ == "IntegrityError":
                return {"msg": str(e)}, 400
            else:
                return {"msg": "Something went wrong"}, 500
        else:
            bill = bill.commit(to_return=True)
            return (
                {
                    "msg": "Billing {} updated successfully".format(bill["id"]),
                    "balance": "{}".format(bill["balance"]),
                },
                201,
            )

    def delete(self):
        try:
            id = request.args.get("id", default=0, type=int)
            if id == 0:
                return {"message": "id is required"}, 400
            bill = BillingModel.find_by(id=id)
            bill.delete_from_db()
        except:
            if bill:
                bill.rollback()
            return {"message": "Something went wrong"}, 500
        else:
            if bill:
                bill.commit()
            return {"message": "billing deleted successfully!"}, 200


class FilterBilling(Resource):
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
            users, pages = filter("billing", value, offset, limit, filter_by)
        except (ValueError, Exception) as e:
            if e.__class__.__name__ == "ValueError":
                return {"msg": str(e)}, 400
            else:
                return {"msg": str(e)}, 500
        else:
            return (
                {"bills": [user.json() for user in users], "pages": str(pages),},
                200,
                {"Content-Type": "application/json"},
            )


#    @validate()
#    def get(self, filter_by: str):
#        if filter_by is None:
#            return {"message": "filter is required"}, 400
#        page = request.args.get("page", default=1, type=int)
#        limit = request.args.get("limit", default=10, type=int)
#        value = request.args.get("value", default=None, type=str)
#        offset = (page - 1) * limit
#        bills, pages = filter('billing', value=value, filter_by=filter_by, offset=offset, limit=limit)
#        if len(bills) == 0:
#            pages = 0
#        return {
#            "bills": [bill.json() for bill in bills],
#            "pages": str(pages),
#        }, 200
