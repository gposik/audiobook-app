from db import db
from flask import request, url_for
from requests import Response
from models.base import BaseModel
from libs.mailgun import Mailgun


class UserModel(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User {self.username}"

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    def send_confirmation_email(self) -> Response:
        # http://127.0.0.1:5000/
        link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        subject = "Registration confirmation."
        text = f"Please click the link to confirm your registration: {link}"
        html = f'<html>Please click the link to confirm your registration: <a href="{link}">{link}</a></html>'

        Mailgun.send_email([self.email], subject, text, html)
