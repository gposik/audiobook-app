import re
from ma import ma
from marshmallow import (
    INCLUDE,
    Schema,
    fields,
    post_load,
    validates,
    ValidationError,
    validate,
)
from models.user import UserModel
from schemas.base import RequestPathParamsSchema, RequestQueryParamsSchema


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id",)
        include_fk = True
        load_instance = True


class UserRegisterSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=True)

    @post_load
    def make_user(self, in_data, **kwargs):
        return UserModel(**in_data)

    @validates("password")
    def validate_password(self, value):
        if len(value) < 6 or len(value) > 12:
            raise ValidationError("Password length must be between 6 and 12 characters")
        if not any(c.islower() for c in value):
            raise ValidationError(
                "Password should contain at least one lower case character"
            )
        if not any(c.isupper() for c in value):
            raise ValidationError(
                "Password should contain at least one upper case character"
            )

    @validates("email")
    def validate_email(self, value):
        email_format = "^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$"
        if not re.match(email_format, value):
            raise ValidationError("Email format is not valid")


class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class UserSubtaskPathSchema(RequestPathParamsSchema):
    user_id = fields.Int(
        description="The id of the user.",
        validate=validate.Range(min=1, max=9999),
        required=True,
    )
    subtask_id = fields.Int(
        description="The id of the subtask.",
        validate=validate.Range(min=1, max=9999),
        required=True,
    )
