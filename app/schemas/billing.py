from typing import Optional
from pydantic import BaseModel, validator
from flask_jwt_extended import get_jwt_identity


class BillingSchema(BaseModel):
    user_id: int
    balance: Optional[float]
    billing_address: Optional[str]

    @validator("billing_address")
    def validate_billing_address(cls, v):
        if v is None:
            raise ValueError("billing_address is required")
        return v

    @validator("balance")
    def check_balance(cls, v):
        if float(v) == float(0):
            raise ValueError("balance can not be 0")
        else:
            return v

    @validator("user_id")
    def check_user_id(cls, v):
        if isinstance(v, int):
            return v
        else:
            raise ValueError("user_id must be an integer")


class UpdateBillingSchema(BillingSchema):
    user_id: Optional[int]
    id: Optional[int]
    balance: Optional[float]
    billing_address: Optional[str]

    @validator("id")
    def check_id(cls, v):
        if v is None:
            return v
        elif isinstance(v, int):
            return v
        else:
            raise ValueError("id must be an integer")
