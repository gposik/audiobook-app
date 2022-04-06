from typing import List
from db import db


class AudiobookModel(db.Model):
    __tablename__ = "audiobooks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    author = db.Column(db.String(80), nullable=False)
    pdf_file = db.Column(db.LargeBinary, unique=True)  # nullable=False
    audio_file = db.Column(db.LargeBinary, unique=True)

    def __repr__(self):
        return f"Audiobook named '{self.name}' from author '{self.author}'"

    @classmethod
    def find_by_id(cls, _id: int) -> "AudiobookModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_name(cls, name: str) -> "AudiobookModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["AudiobookModel"]:
        return cls.query.all()

    def save_to_db(self) -> "None":
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> "None":
        db.session.delete(self)
        db.session.commit()
