from uuid import uuid4
from time import time
from db import db
from models.base import BaseModel

CONFIRMATION_EXPIRATION_DELTA = 1800  # 30 minutes


class ConfirmationModel(BaseModel):
    __tablename__ = "confirmations"

    id = db.Column(db.String(50), primary_key=True)
    expired_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expired_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return super().find_by_id(_id)

    @classmethod
    def find_by_id_or_404(cls, _id: str) -> "ConfirmationModel":
        return super().find_by_id_or_404(_id)

    @property
    def expired(self) -> bool:
        return time() > self.expired_at

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expired_at = int(time())
            self.save_to_db()
