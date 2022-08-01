from ma import ma
from models.audiobook import AudiobookModel
from marshmallow import EXCLUDE


class AudiobookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AudiobookModel
        dump_only = ("id", "audio_file", "book_file")
        load_instance = True
        unknown = EXCLUDE
