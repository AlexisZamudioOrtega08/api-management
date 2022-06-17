import re
from typing import Optional
from common.util import is_email
from pydantic import BaseModel, validator


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    address: str

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 8:
            raise ValueError("username must be at least 8 characters")
        else:
            regex = re.compile(r"^[a-zA-Z0-9_]+$")
            if not regex.match(v):
                raise ValueError("username must be alphanumeric")
            return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        else:
            pattern = "Must be at least 8 charactes and at least one character of the following pattern [A-Z][a-z][0-9][@$!%*#?&]."
            patt = re.compile(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
            )
            if re.search(patt, v):
                return v
            else:
                raise ValueError("Password must match the pattern: " + pattern)

    @validator("email")
    def validate_email(cls, v):
        if is_email(v):
            return v
        else:
            raise ValueError("Email address is not valid")

    @validator("address")
    def validate_address(cls, v):
        if len(v) < 16:
            raise ValueError("please validate your address")
        return v


class FilterUser(BaseModel):
    value: Optional[str]


class UpdateUserSchema(UserSchema):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    identifier: Optional[str]
    email: Optional[str]
    address: Optional[str]
    role: Optional[str]

    @validator("identifier")
    def validate_identifier(cls, v):
        if v is None:
            raise ValueError("identifier is required")
        else:
            return v

    @validator("role")
    def validate_role(cls, v):
        if v == None:
            return v
        else:
            if int(v) not in (1, 2):
                raise ValueError("role must be 1, 2")
            return v
