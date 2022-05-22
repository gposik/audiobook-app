from db import db
from sqlalchemy import and_
from sqlalchemy.ext.hybrid import hybrid_property
from models.base import BaseModel
from models.user import UserModel
from models.subtask import SubtaskModel


class CollaboratorModel(BaseModel):
    __tablename__ = "collaborators"

    user = db.relationship("UserModel")
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    subtasks = db.relationship("SubtaskModel", backref="collaborator", lazy="dynamic")

    def __repr__(self):
        return f"Collaborator <id:{self.id}>"

    def get_current_subtask(self) -> "SubtaskModel":
        return SubtaskModel.query.filter_by(id=self.subtask_id).first()

    @hybrid_property
    def current_subtask(self) -> "SubtaskModel":
        return self.subtasks.filter(
            and_(SubtaskModel.is_completed == False, SubtaskModel.is_expired == False)
        ).first()
