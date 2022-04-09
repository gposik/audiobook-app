from typing import List
from db import db
from models.subtask import SubtaskModel
from models.audiobook import AudiobookModel
from models.timestamp import Timestamp
from sqlalchemy.orm import backref


class TaskModel(Timestamp, db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    collaborators_number = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    audiobook_id = db.Column(
        db.Integer, db.ForeignKey("audiobooks.id"), nullable=False, unique=True
    )
    audiobook = db.relationship(
        "AudiobookModel", backref=backref("task", uselist=False)
    )
    subtasks = db.relationship("SubtaskModel")

    def __repr__(self):
        return f"Task <id:{self.id}>"

    @classmethod
    def find_by_id(cls, _id: int) -> "TaskModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_audiobook_id(cls, audiobook_id) -> "TaskModel":
        return cls.query.filter_by(audiobook_id=audiobook_id).first()

    @classmethod
    def find_all(cls) -> List["TaskModel"]:
        return cls.query.all()

    def get_available_subtasks(self) -> List["SubtaskModel"]:
        return SubtaskModel.query.filter_by(is_completed=False, task_id=self.id).all()

    def get_subtask_by_id(self, subtask_id) -> "SubtaskModel":
        return next((x for x in self.subtasks if x.id == subtask_id), None)

    def save_to_db(self) -> "None":
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> "None":
        db.session.delete(self)
        db.session.commit()
