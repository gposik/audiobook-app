from flask import Blueprint, jsonify
from marshmallow import ValidationError
from exceptions import APIError


error_bp = Blueprint("errors", __name__)


@error_bp.app_errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({"messages": err.messages}), 400


@error_bp.app_errorhandler(APIError)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
