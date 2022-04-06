from ma import ma
from models.audiobook import AudiobookModel


class AudiobookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AudiobookModel
        dump_only = ("id",)
        load_instance = True
