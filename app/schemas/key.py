from pydantic import BaseModel, validator


class KeySchema(BaseModel):
    user_id: int

    @validator("user_id")
    def validate_user_id(cls, v):
        if v < 0:
            raise ValueError("User ID must be a positive integer")
        return v
