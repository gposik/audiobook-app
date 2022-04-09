from db import db
from models.timestamp import Timestamp


class SubtaskModel(Timestamp, db.Model):
    __tablename__ = "subtasks"

    id = db.Column(db.Integer, primary_key=True)
    fragment = db.Column(db.Text)  # nullable=False
    is_completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), default=None)

    def __repr__(self):
        return f"Subtask <id:{self.id}>"

    @classmethod
    def find_by_id(cls, _id: int) -> "SubtaskModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> "None":
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> "None":
        db.session.delete(self)
        db.session.commit()
