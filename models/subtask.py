from db import db
from models.base import BaseModel
from models.timestamp import Timestamp


class SubtaskModel(Timestamp, BaseModel):
    __tablename__ = "subtasks"

    fragment = db.Column(db.Text)  # nullable=False
    is_completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), default=None)

    def __repr__(self):
        return f"Subtask <id:{self.id}>"
