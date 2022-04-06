from flask import Blueprint, jsonify
from marshmallow import ValidationError

error_bp = Blueprint("errors", __name__)


@error_bp.app_errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({"messages": err.messages}), 400
