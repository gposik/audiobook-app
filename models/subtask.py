from db import db
from models.base import BaseModel
from models.timestamp import Timestamp
from sqlalchemy.ext.hybrid import hybrid_property


class SubtaskModel(Timestamp, BaseModel):
    __tablename__ = "subtasks"

    fragment = db.Column(db.Text, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), default=None)
    collaborator_id = db.Column(
        db.Integer, db.ForeignKey("collaborators.id"), nullable=True
    )

    def __repr__(self):
        return f"Subtask <id:{self.id}>"

    @hybrid_property
    def is_valid(self) -> bool:
        """Checks wheater the subtasks is still available. This is means is not taken, expired or completed"""
        return (
            not self.is_completed
            and not self.is_expired
            and self.collaborator_id is None
        )
