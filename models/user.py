from db import db
from models.base import BaseModel
from models.subtask import SubtaskModel


class UserModel(BaseModel):
    __tablename__ = "users"

    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    subtask_id = db.Column(db.Integer, db.ForeignKey("subtasks.id"))

    def __repr__(self):
        return f"User {self.username}"

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    def get_current_subtask(self) -> "SubtaskModel":
        return SubtaskModel.query.filter_by(id=self.subtask_id).first()
