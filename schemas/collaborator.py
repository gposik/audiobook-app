from ma import ma
from marshmallow import fields, validate
from models.collaborator import CollaboratorModel
from schemas.base import RequestPathParamsSchema
from schemas.subtask import SubtaskSchema


class CollaboratorSchema(ma.SQLAlchemyAutoSchema):
    current_subtask = fields.Nested(SubtaskSchema, only=("id",), data_key="subtask")

    class Meta:
        model = CollaboratorModel
        exclude = ["subtasks"]
        dump_only = ("id", "current_subtask")
        load_only = ("user_id",)
        include_fk = True
        load_instance = True


class CollaboratorSubtaskPathSchema(RequestPathParamsSchema):
    collaborator_id = fields.Int(
        description="The id of the collaborator.",
        validate=validate.Range(min=1, max=9999),
        required=True,
    )
    subtask_id = fields.Int(
        description="The id of the subtask.",
        validate=validate.Range(min=1, max=9999),
        required=True,
    )
