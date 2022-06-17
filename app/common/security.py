from flask import Response, make_response
from flask_jwt_extended import get_jwt
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies

from datetime import datetime
from datetime import timedelta, timezone

from common.util import is_email
from models.user import User as UserModel


def authenticate(identifier: str, password: str) -> str:
    """
    This function is called when a user attempts to log in.
    :param identifier: The user's username or email address.
    :param password: Password provide that should match the user's password.
    :return: A JSON Web Token if the user was successfully authenticated.
    """
    response = {"msg": ""}
    is_mail = is_email(identifier)
    if is_mail:
        user = UserModel.find_by(email=identifier)
    else:
        user = UserModel.find_by(username=identifier)
    if user is None:
        raise ValueError("Invalid identifier or password.")
    elif user and user.check_password(str(user.password), str(password)):
        response["msg"] = "Successfully logged in."
        response = make_response(response, 200)
        token = create_access_token(identity=user.identity())
        set_access_cookies(response, token)
        return response
    else:
        raise ValueError("Invalid identifier or password.")


def refresh_expiration(response: Response) -> Response:
    """
    This function is used to refresh the JWT token expiration.
    :param response: The response object.
    :return: The response object with the new JWT token.
    """
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


def expire_token(response: Response) -> Response:
    """
    This function is used to expire the JWT token.
    :param response: The response object.
    :return: The response object with the expired JWT token.
    """
    try:
        unset_jwt_cookies(response)
    except (RuntimeError, KeyError):
        return response
    else:
        return response
