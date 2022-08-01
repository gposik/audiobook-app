from models.base import BaseModel
from db import db


class AudiobookModel(BaseModel):
    __tablename__ = "audiobooks"

    name = db.Column(db.String(80), nullable=False, unique=True)
    author = db.Column(db.String(80), nullable=False)
    book_file = db.Column(db.String(80), unique=True)
    audio_file = db.Column(db.String(512), unique=True)

    def __repr__(self):
        return f"Audiobook named '{self.name}' from author '{self.author}'"

    @classmethod
    def find_by_name(cls, name: str) -> "AudiobookModel":
        return cls.query.filter_by(name=name).first()
