from ma import ma
from marshmallow import EXCLUDE, fields
from models.subtask import SubtaskModel
from schemas.base import RequestQueryParamsSchema


class SubtaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SubtaskModel
        dump_only = ("id",)
        load_only = ("task_id",)
        include_fk = True
        load_instance = True


class SubtaskQuerySchema(RequestQueryParamsSchema):
    class Meta:
        unknown = EXCLUDE

    is_completed = fields.Boolean(description="Subtask status.")
