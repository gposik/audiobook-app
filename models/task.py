from io import StringIO
from typing import List
from db import db
from sqlalchemy.orm import backref
from sqlalchemy.ext.hybrid import hybrid_property
from models.base import BaseModel
from models.subtask import SubtaskModel
from models.audiobook import AudiobookModel
from models.timestamp import Timestamp


class TaskModel(Timestamp, BaseModel):
    __tablename__ = "tasks"

    audiobook_id = db.Column(
        db.Integer, db.ForeignKey("audiobooks.id"), nullable=False, unique=True
    )
    audiobook = db.relationship(
        "AudiobookModel",
        backref=backref("task", uselist=False, cascade="all, delete-orphan"),
    )
    subtasks = db.relationship(
        "SubtaskModel",
        backref=backref("task", uselist=False),
    )
    fragments_ranges = []

    def __repr__(self):
        return f"Task <id:{self.id}>"

    @classmethod
    def find_by_audiobook_id(cls, audiobook_id: int) -> "TaskModel":
        return cls.query.filter_by(audiobook_id=audiobook_id).first()

    @hybrid_property
    def is_completed(self) -> bool:
        return all(x.is_completed for x in self.subtasks)

    @hybrid_property
    def available_subtasks(self) -> List["SubtaskModel"]:
        return [x for x in self.subtasks if x.collaborator_id is None]

    def get_subtask_by_id(self, subtask_id: int) -> "SubtaskModel":
        return next((x for x in self.subtasks if x.id == subtask_id), None)

    def get_fragments_from_text(self, text: str) -> List[str]:
        fragments = []

        book_iter = StringIO(text)
        last = 0
        for fragment in self.fragments_ranges:
            init = fragment["first_line"]
            finish = fragment["last_line"]

            for _ in range(last, init):
                next(book_iter)

            frg = ""
            for _ in range(init, finish + 1):
                frg += book_iter.readline()

            last = finish

            fragments.append(frg)

        return fragments
