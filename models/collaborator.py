from db import db
from models.base import BaseModel
from models.user import UserModel
from models.subtask import SubtaskModel


class CollaboratorModel(BaseModel):
    __tablename__ = "collaborators"

    user = db.relationship("UserModel")
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    subtask_id = db.Column(
        db.Integer, db.ForeignKey("subtasks.id"), nullable=True, unique=True
    )

    def __repr__(self):
        return f"Collaborator <id:{self.id}>"

    def get_current_subtask(self) -> "SubtaskModel":
        return SubtaskModel.query.filter_by(id=self.subtask_id).first()
