import re

from pydantic import BaseModel, PositiveInt, constr, field_validator


class UserSchema(BaseModel):
    login: str
    password: str

    @field_validator('login', mode='before')
    def validate_username(cls, v):
        if not v:
            raise ValueError("Username cannot be empty.")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username can only contain letters, numbers, and underscores.")
        return v

    @field_validator('password', mode='before')
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password cannot be empty.")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v



class CreateUserSchema(UserSchema):
    is_admin: bool = False


class TopUpScheme(BaseModel):
    amount: PositiveInt


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
