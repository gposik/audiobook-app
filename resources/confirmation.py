from datetime import datetime
import traceback

from flask import make_response, render_template
from flask_restful import Resource
from libs.mailgun import MailgunException
from libs.strings import gettext

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


RESOURCE_NAME = "Confirmation"

confirmation_schema = ConfirmationSchema()
confirmation_schema_list = ConfirmationSchema(many=True)


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Return confirmation HTML page."""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404

        if confirmation.is_expired:
            return {"message": gettext("confirmation_link_expired")}, 400

        if confirmation.is_confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400

        confirmation.is_confirmed = True
        confirmation.save_to_db()

        response = make_response(
            render_template("confirmation_page.html", email=confirmation.user.email)
        )
        response.headers["Content-Type"] = "text/html"
        return response


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id):
        """Returns confirmations for a given user. Used for testing purpouse."""
        user = UserModel.find_by_id_or_404(user_id)
        sorted_user_confirmations = user.confirmation.order_by(
            ConfirmationModel.expired_at
        )
        return {
            "current_time": str(datetime.utcnow()),
            "confirmations": confirmation_schema_list.dump(sorted_user_confirmations),
        }, 200

    @classmethod
    def post(cls, user_id):
        """Resend confirmation email"""
        user = UserModel.find_by_id_or_404(user_id)

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.is_confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            # user.send_confirmation_email()
            return {"message": gettext("confirmation_resend_successful")}, 201
        except MailgunException as e:
            return {"message": e.messages}, 500
        except:
            traceback.print_exc()
            return {"message": gettext("confirmation_resend_failed")}, 500
