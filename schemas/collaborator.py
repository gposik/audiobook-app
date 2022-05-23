from marshmallow import fields, pre_dump, validate
from models.collaborator import CollaboratorModel
from models.subtask import SubtaskModel
from schemas.base import RequestPathParamsSchema
from ma import ma
from schemas.subtask import SubtaskSchema


class CollaboratorSchema(ma.SQLAlchemyAutoSchema):
    subtasks = fields.Nested(SubtaskSchema, only=("id",), data_key="subtask")

    class Meta:
        model = CollaboratorModel
        dump_only = ("id",)
        load_only = ("user_id",)
        include_fk = True
        load_instance = True

    @pre_dump
    def only_current_subtask(self, collaborator: CollaboratorModel, **kwargs):
        if collaborator.current_subtask:
            collaborator.subtasks = [collaborator.current_subtask]
        return collaborator


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
