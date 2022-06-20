from flask import Flask
from flask import make_response
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.key import Key, FilterKey
from resources.user import User, FilterUser
from resources.billing import Billing, FilterBilling
from resources.auth import Login, Logout

from config import config
from database.db import db

app = Flask(__name__)
api = Api(app)
api_prefix = config["default"].API_PREFIX

# ------------- CREATE DATABASE --------------#
@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(Login, "{}/login".format(api_prefix), methods=["POST"])
api.add_resource(Logout, "{}/logout".format(api_prefix), methods=["POST"])
api.add_resource(
    FilterUser,
    "{}/users/<filter_by>".format(api_prefix),
    endpoint="user",
    methods=["GET"],
)
api.add_resource(
    User,
    "{}/users".format(api_prefix),
    endpoint="users",
    methods=["GET", "PUT", "POST", "DELETE"],
)
api.add_resource(
    FilterKey,
    "{}/keys/<string:filter_by>".format(api_prefix),
    endpoint="key",
    methods=["GET"],
)
api.add_resource(
    Key, "{}/keys".format(api_prefix), endpoint="keys", methods=["GET", "POST", "DELETE"]
)
api.add_resource(
    FilterBilling,
    "{}/billings/<string:filter_by>".format(api_prefix),
    endpoint="billing",
    methods=["GET"],
)
api.add_resource(
    Billing,
    "{}/billings".format(api_prefix),
    endpoint="billings",
    methods=["GET", "POST", "PUT", "DELETE"],
)


def status_400(error):
    return make_response({"msg": str(error)}, 400)


def status_401(error):
    return make_response({"msg": "Unauthorized"}, 401)


def status_403(error):
    return make_response({"msg": "Forbidden"}, 403)


def status_404(error):
    return make_response({"msg": "Path not found"}, 404)


if __name__ == "__main__":
    # import configuration
    app.config.from_object(config["default"])
    # secret key
    app.secret_key = config["default"].KEY
    # initialize jwt
    jwt = JWTManager(app)
    # initialize the database
    db.init_app(app)
    # register the error handler
    app.register_error_handler(400, status_400)
    app.register_error_handler(403, status_403)
    app.register_error_handler(404, status_404)
    jwt.unauthorized_loader(status_401)
    # run the app
    app.run(host="0.0.0.0", port=5000)
