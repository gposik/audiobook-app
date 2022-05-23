from asyncio import current_task
from flask import request
from flask_restful import Resource
from sqlalchemy import exc
from db import db
from libs.strings import gettext
from utils.api_utils import request_schemas_load
from models.collaborator import CollaboratorModel
from models.user import UserModel
from models.subtask import SubtaskModel
from schemas.collaborator import CollaboratorSchema, CollaboratorSubtaskPathSchema
from schemas.subtask import SubtaskSchema


RESOURCE_NAME = "Collaborator"

collaborator_schema = CollaboratorSchema()
collaborator_list_schema = CollaboratorSchema(many=True)
subtask_schema = SubtaskSchema()
subtask_list_schema = SubtaskSchema(many=True, exclude=("collaborator_id",))


class Collaborator(Resource):
    @classmethod
    def get(cls, collaborator_id: int):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)
        return collaborator_schema.dump(collaborator), 200

    def post(cls):
        collaborator_json = request.get_json()
        collaborator = collaborator_schema.load(collaborator_json)

        user = UserModel.find_by_id_or_404(collaborator.user_id)
        if user.collaborator:
            return {
                "message": "The user with user_id <{}> is already a collaborator".format(
                    user.id
                )
            }, 400

        try:
            collaborator.save_to_db()
        except exc.IntegrityError:
            db.session.rollback()
            return {"messages": gettext("failed_to_save_to_db")}, 409

        return collaborator_schema.dump(collaborator), 201


class CollaboratorList(Resource):
    @classmethod
    def get(cls):
        return {
            "collaborators": collaborator_list_schema.dump(CollaboratorModel.find_all())
        }, 200


class CollaboratorSubtask(Resource):
    @classmethod
    def get(cls, collaborator_id: int):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)

        subtask = collaborator.current_subtask
        if not subtask:
            return {"message": gettext("collaborator_subtask_not_found")}, 404

        return subtask_schema.dump(subtask), 200

    @classmethod
    def post(cls, collaborator_id: int, subtask_id: int):
        request_schemas_load([CollaboratorSubtaskPathSchema()])

        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)

        current_subtask = collaborator.current_subtask
        if current_subtask:
            return {
                "message": gettext("collaborator_already_has_subtask").format(
                    current_subtask.id
                )
            }, 400

        subtask = SubtaskModel.find_by_id_or_404(subtask_id)

        if not subtask.is_valid:
            return {"message": gettext("subtask_not_valid")}, 400

        subtask.collaborator_id = collaborator.id
        subtask.save_to_db()

        return {"message": gettext("collaborator_subtask_assigned")}, 200


class CollaboratorHistory(Resource):
    @classmethod
    def get(cls, collaborator_id: int):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)

        return subtask_list_schema.dump(collaborator.subtasks), 200
