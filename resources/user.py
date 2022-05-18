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
from libs.mailgun import MailgunException
from libs.strings import gettext
from models.user import UserModel
from schemas.user import UserSchema
from models.confirmation import ConfirmationModel

RESOURCE_NAME = "User"

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            return {
                "message": gettext("entity_with_already_exists").format(
                    RESOURCE_NAME, "username"
                )
            }, 400

        if UserModel.find_by_email(user.email):
            return {
                "message": gettext("entity_with_already_exists").format(
                    RESOURCE_NAME, "email"
                )
            }, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            # user.send_confirmation_email()
            return {"message": gettext("user_registered")}, 201
        except MailgunException as e:
            db.session.rollback()
            return {"message": e.messages}, 500
        except:
            traceback.print_exc()
            db.session.rollback()
            return {
                "message": gettext("entity_failed_to_create").format(RESOURCE_NAME)
            }, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating user_data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404
        user.delete_from_db()
        return {"message": gettext("entity_deleted").format(RESOURCE_NAME)}, 200


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
            return {"message": gettext("user_not_confirmed").format(user.email)}, 400
        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
