from pydantic import BaseModel, validator


class AuthSchema(BaseModel):
    identifier: str
    password: str

    @validator("identifier")
    def username_validator(cls, v):
        if v is None:
            raise ValueError("username is required")
        return v

    @validator("password")
    def password_validator(cls, v):
        if v is None:
            raise ValueError("password is required")
        return v
