import re
from typing import Optional, Tuple

from models.key import Key as KeyModel
from models.user import User as UserModel
from models.billing import Billing as BillingModel

from flask_jwt_extended import get_jwt_identity


types = {
    "user": [["UserModel.", "u_"], ("id", "username", "email", "date", "role", "all")],
    "billing": [["BillingModel.", "b_"], ("id", "user_id", "date", "all")],
    "key": [["KeyModel.", "k_"], ("id", "billing_id", "date", "all")],
}

filters = {
    "u_username": "filtering(offset, limit, username=value)",
    "u_email": "filtering(offset, limit, email=value)",
    "u_date": "filtering(offset, limit, updated_at=value)",
    "u_id": "filtering(offset, limit, id=value)",
    "u_role": "filtering(offset, limit, role=value)",
    "u_all": "filtering(offset, limit, all=True)",
    "b_user_id": "filtering(offset, limit, user_id=value)",
    "b_date": "filtering(offset, limit, updated_at=value)",
    "b_id": "filtering(offset, limit, id=value)",
    "b_all": "filtering(offset, limit, all=True)",
    "k_billing_id": "filtering(offset, limit, billing_id=value)",
    "k_date": "filtering(offset, limit, updated_at=value)",
    "k_id": "filtering(offset, limit, id=value)",
    "k_all": "filtering(offset, limit, all=True)",
}

roles = {
    "1": ["def", ("first_name", "last_name", "email", "password", "address")],
    "2": ["adm", ("first_name", "last_name", "email", "password", "address", "role")],
}


def is_admin() -> bool:
    """
    Check if the user is an admin.
    """
    user = get_jwt_identity()
    role = str(user.get("role"))
    if roles[role][0] == "adm":
        return True
    else:
        return False


def is_email(identifier: str) -> bool:
    """
    Check if the given email is valid.
    :param identifier: To define if is mail.
    :return: True if the email is valid, False otherwise.
    """
    if identifier is None:
        return False
    is_email = re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", identifier)
    if is_email:
        return True
    else:
        return False


def is_id(identifier: str) -> bool:
    """
    Check if the given email is valid.
    :param identifier: To define if is mail.
    :return: True if the email is valid, False otherwise.
    """
    if identifier is None:
        return False
    is_id = re.search("^[0-9]+$", identifier)
    return is_id


def is_username(identifier: str) -> bool:
    """
    Check if the given username is valid.
    :param identifier: To define if is username.
    :return: True if the username is valid, False otherwise.
    """
    if identifier is None:
        return False
    if is_email(identifier) or is_id(identifier):
        return False
    else:
        return True


def create_sentence(_type: str, _filter: str) -> str:
    """
    Create a sentence to query the database.
    """
    filter = None
    _type = types[_type]
    if _filter not in _type[1]:
        raise ValueError(
            "Invalid filter. Expected one of: {}".format([key for key in _type[1]])
        )
    else:
        prefix = _type[0][1] + _filter
        filter = _type[0][0] + filters[prefix]
    return filter


def filter(
    _type: str,
    value: str or int,
    offset: Optional[int] = 1,
    limit: Optional[int] = 10,
    filter_by: Optional[str] = None,
) -> Tuple[list, int]:
    """
    Filter the users by the given parameters.
    :param _type: The type of the object to filter.
    :param value: The value to filter by.
    :param offset: The offset to start the query.
    :param limit: The limit of the query.
    :param filter_by: The filter to apply.
    :return: The users found and the total number of users.
    """
    if _type not in types:
        raise ValueError(
            "Invalid type. Expected one of: {}".format([key for key in types.keys()])
        )
    else:
        sentence = create_sentence(_type, filter_by)
        users, count = eval(sentence)
        if count % limit == 0:
            pages = count // limit
        else:
            pages = count // limit + 1
        return users, pages


# ----------------- USER HELPER ----------------- #
class UserHelper:
    def __init__(self):
        self.message = ""
        self.permissions = None
        self.user = None
        self.id = None
        self.identifier = None
        self.expire = False

    def set_permissions(self) -> None:
        """
        Check if the user is allowed to modify an existing user.
        :return: True if the user is allowed, False otherwise.
        """
        identity = get_jwt_identity()
        role, id = identity.get("role"), identity.get("id")
        self.permissions = roles.get(str(role))
        self.id = id
        self.expire = False

    def get_user(self, body: dict) -> None:
        self.user = None
        role = self.permissions[0]
        if role == "def":
            self.user = UserModel.find_by(id=self.id)

        elif role == "adm":
            if is_email(body.get("identifier")):
                self.user = UserModel.find_by(email=body.get("identifier"))
                if self.user is None:
                    raise ValueError("User not found.")
                self.identifier = "email"
                if body.get(self.identifier):
                    raise ValueError(
                        "You can not modify the email since is provided as identifier."
                    )
            elif is_id(body.get("identifier")):
                self.user = UserModel.find_by(id=body.get("identifier"))
                if self.user is None:
                    raise ValueError("User not found.")
                self.identifier = "id"
                if body.get(self.identifier):
                    raise ValueError(
                        "You can not modify the id since is primary identifier."
                    )
            elif is_username(body.get("identifier")):
                self.user = UserModel.find_by(username=body.get("identifier"))
                if self.user is None:
                    raise ValueError("User not found.")
                self.identifier = "username"
                if (
                    body.get(self.identifier)
                    or body.get("identifier") != self.user.username
                ):
                    raise ValueError(
                        "You can not modify the username since is provided as identifier."
                    )

            else:
                raise ValueError("Invalid identifier.")
        else:
            raise ValueError("Invalid role.")

    @classmethod
    def update_body(cls, body: dict) -> Tuple[UserModel, bool]:
        _body = body.dict()
        cls.set_permissions(cls)
        cls.get_user(cls, _body)
        _user = cls.user.json()
        keys = _body.keys()
        if _body.get("role") != None and cls.permissions[0] not in ("adm"):
            raise ValueError("Forbidden.")
        flag = False
        for key in keys:
            if key in cls.permissions[1] and _body[key] != None:
                if key == "password":
                    body.password = UserModel.crate_hash(body.password)
                    if cls.permissions[0] == "def":
                        cls.expire = True
                if _body[key] != _user[key]:
                    exec("cls.user.{} = body.{}".format(key, key))
                    flag = True
        return cls.user, flag, cls.expire

    @classmethod
    def find_duplicate(cls, body: dict) -> Tuple[bool, str]:
        user = UserModel.find_by(username=body.username)
        if user:
            return True, "Username already exists"
        user = UserModel.find_by(email=body.email)
        if user:
            return True, "Email already exists"

        return False, None

    def check_status(self, user_id: int) -> bool:
        try:
            if self.message["billing"] == "fail":
                user = UserModel.find_by(id=user_id)
                if user:
                    user.delete_from_db()
                    user.commit()
        except:
            self.message["user"] = "fail"
        finally:
            if self.message["user"] == "fail" or self.message["billing"] == "fail":
                return {"msg": "An error occurred creating the user."}, 500
            elif (
                self.message["user"] == "success"
                and self.message["billing"] == "success"
            ):
                return {"msg": "User created successfully!"}, 201

    @classmethod
    def post_billing(cls, message, user_id):
        try:
            cls.message = message
            if user_id:
                billing = BillingModel(user_id=user_id)
                billing.save_to_db()
        except Exception as e:
            if billing:
                billing.rollback()
            cls.message["billing"] = "fail"
        else:
            if billing:
                billing.commit()
            cls.message["user"] = "success"
            cls.message["billing"] = "success"
            return cls.check_status(cls, user_id)
