from flask import request
from flask_restful import Resource
from sqlalchemy import exc
from db import db
from models.collaborator import CollaboratorModel
from models.user import UserModel
from schemas.collaborator import CollaboratorSchema, CollaboratorSubtaskPathSchema
from utils.api_utils import request_schemas_load
from models.subtask import SubtaskModel
from schemas.subtask import SubtaskSchema


RESOURCE_NAME = "Collaborator"
NOT_CURRENT_SUBTASK = "This user has no subtask assigned"
SUBTASK_ASSIGNED_SUCCESSFULLY = "The subtask was successfully assigned"

collaborator_schema = CollaboratorSchema()
collaborator_list_schema = CollaboratorSchema(many=True)
subtask_schema = SubtaskSchema()


class Collaborator(Resource):
    @classmethod
    def get(cls, collaborator_id):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)
        return collaborator_schema.dump(collaborator), 200

    def post(cls):
        collaborator_json = request.get_json()
        collaborator = collaborator_schema.load(collaborator_json)

        UserModel.find_by_id_or_404(collaborator.user_id)
        if collaborator.subtask_id:
            SubtaskModel.find_by_id_or_404(collaborator.subtask_id)

        try:
            collaborator.save_to_db()
        except exc.IntegrityError:
            db.session.rollback()
            return {"messages": "Something went wrong when saving to database"}, 409

        return collaborator_schema.dump(collaborator), 201


class CollaboratorList(Resource):
    @classmethod
    def get(cls):
        return {
            "collaborators": collaborator_list_schema.dump(CollaboratorModel.find_all())
        }, 200


class CollaboratorSubtask(Resource):
    @classmethod
    def get(cls, collaborator_id):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)

        subtask = collaborator.get_current_subtask()
        if not subtask:
            return {"message": NOT_CURRENT_SUBTASK}, 404

        return subtask_schema.dump(subtask), 200

    @classmethod
    def post(cls, collaborator_id, subtask_id):
        request_schemas_load([CollaboratorSubtaskPathSchema()])

        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)
        subtask = SubtaskModel.find_by_id_or_404(subtask_id)

        collaborator.subtask_id = subtask.id
        collaborator.save_to_db()

        return {"message": SUBTASK_ASSIGNED_SUCCESSFULLY}, 200
