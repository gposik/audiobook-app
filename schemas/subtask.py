from ma import ma
from marshmallow import EXCLUDE, fields
from models.subtask import SubtaskModel
from schemas.base import RequestQueryParamsSchema


class SubtaskSchema(ma.SQLAlchemyAutoSchema):
    is_expired = fields.Bool()

    class Meta:
        model = SubtaskModel
        exclude = ["creation_date", "modification_date", "expiration_date"]
        dump_only = ("id", "audio_file")
        load_only = ("task_id",)
        include_fk = True
        load_instance = True
        unknown = EXCLUDE


class SubtaskQuerySchema(RequestQueryParamsSchema):
    class Meta:
        unknown = EXCLUDE

    is_completed = fields.Boolean(description="Subtask status.")
    is_expired = fields.Boolean(description="Subtask expired.")
    _id = fields.Int(descrition="Subtask", data_key="id", attribute="id")
