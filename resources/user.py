import traceback
from db import db
from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
from blacklist import BLACKLIST
from config import (
    ALREADY_EXISTS,
    NOT_FOUND,
    DELETED,
    FAILED_TO_CREATE,
)
from libs.mailgun import MailgunException
from models.user import UserModel
from schemas.user import UserSchema
from models.confirmation import ConfirmationModel

INVALID_CREDENTIALS = "Invalid credentials!"
USER_LOGGED_OUT = "User <id={}> successfully logged out."
SUCCESS_REGISTER_MESSAGE = "Account created succesfully, an activation link has been sent to your email address. Please check"
NOT_CONFIRMED_ERROR = (
    "You have not confirmed registration, please check your email <{}>"
)
RESOURCE_NAME = "User"

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username) or UserModel.find_by_email(
            user.email
        ):
            return {
                "message": ALREADY_EXISTS.format(RESOURCE_NAME, "username or email")
            }, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            # user.send_confirmation_email()
            return {"message": SUCCESS_REGISTER_MESSAGE}, 201
        except MailgunException as e:
            db.session.rollback()
            return {"message": e.messages}, 500
        except:
            traceback.print_exc()
            db.session.rollback()
            return {"message": FAILED_TO_CREATE.format(RESOURCE_NAME)}, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating user_data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND.format(RESOURCE_NAME)}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND.format(RESOURCE_NAME)}, 404
        user.delete_from_db()
        return {"message": DELETED.format(RESOURCE_NAME)}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and (user.password == user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.is_confirmed:
                # identity= is what the identity() function did in security.py—now stored in the JWT
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.email)}, 400
        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
