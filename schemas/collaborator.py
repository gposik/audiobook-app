from marshmallow import fields, validate
from models.collaborator import CollaboratorModel
from schemas.base import RequestPathParamsSchema
from ma import ma


class CollaboratorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CollaboratorModel
        dump_only = ("id",)
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
