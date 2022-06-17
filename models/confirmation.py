from uuid import uuid4
from time import time
from datetime import datetime, timedelta
from sqlalchemy.orm import backref
from db import db
from models.base import BaseModel

CONFIRMATION_EXPIRATION_DELTA = 30  # 30 minutes


def default_expiration():
    return datetime.utcnow() + timedelta(minutes=CONFIRMATION_EXPIRATION_DELTA)


class ConfirmationModel(BaseModel):
    __tablename__ = "confirmations"

    id = db.Column(db.String(50), primary_key=True)
    expired_at = db.Column(db.DateTime, default=default_expiration, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship(
        "UserModel",
        backref=backref("confirmation", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex

    def __repr__(self):
        return f"Confirmation <id:{self.id}>"

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expired_at

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return super().find_by_id(_id)

    @classmethod
    def find_by_id_or_404(cls, _id: str) -> "ConfirmationModel":
        return super().find_by_id_or_404(_id)

    def force_to_expire(self) -> None:
        if not self.is_expired:
            self.expired_at = datetime.utcnow()
            self.save_to_db()
