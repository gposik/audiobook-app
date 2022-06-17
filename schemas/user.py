import re
from ma import ma
from marshmallow import pre_dump, validates, ValidationError, fields
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


class UserSchema(ma.SQLAlchemyAutoSchema):
    confirmation = fields.Nested(ConfirmationSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "confirmation")
        include_fk = True
        load_instance = True

    @pre_dump
    def only_most_recent_confirmation(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user

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
