from time import time
import traceback

from flask import make_response, render_template
from flask_restful import Resource
from libs.mailgun import MailgunException

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

NOT_FOUND = "Confirmation reference not found."
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has already been confirmed."
RESEND_FAILED = "Failed to resend confirmation email"
CONFIRMATION_SUCCESSFUL = "E-mail confirmation successfully re-sent"

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Return confirmation HTML page."""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return (
            make_response(
                render_template("confirmation_page.html"), email=confirmation.user.email
            ),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id):
        """Returns confirmations for a given user. Used for testing purpouse."""
        user = UserModel.find_by_id_or_404(user_id)

        return {
            "current_time": int(time()),
            "confirmations": [
                confirmation_schema.dump(each)
                for each in user.confirmation.order_by(ConfirmationModel.expired_at)
            ],
        }, 200

    @classmethod
    def post(cls, user_id):
        """Resend confirmation email"""
        user = UserModel.find_by_id_or_404(user_id)

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
            confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            # user.send_confirmation_email()
            return {"message": CONFIRMATION_SUCCESSFUL}, 201
        except MailgunException as e:
            return {"message": e.messages}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAILED}, 500
