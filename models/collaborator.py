from db import db

from sqlalchemy import and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref

from models.base import BaseModel
from models.user import UserModel
from models.subtask import SubtaskModel


class CollaboratorModel(BaseModel):
    __tablename__ = "collaborators"

    user = db.relationship("UserModel", backref=backref("collaborator", uselist=False))
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    subtasks = db.relationship("SubtaskModel", backref="collaborator", lazy="dynamic")

    def __repr__(self):
        return f"Collaborator <id:{self.id}>"

    @hybrid_property
    def current_subtask(self) -> SubtaskModel:
        return self.subtasks.filter(
            and_(SubtaskModel.is_completed == False, SubtaskModel.is_expired == False)
        ).first()
