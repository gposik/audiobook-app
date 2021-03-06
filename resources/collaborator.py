from db import db
from uuid import uuid4

from flask import request
from flask_restful import Resource
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import exc
from libs.file_helper import AUDIO_CONF, FileHelper

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


class Collaborator(MethodResource, Resource):
    @doc(description="My First GET Awesome API.", tags=["Awesome"])
    @marshal_with(collaborator_schema, apply=False)
    def get(self, collaborator_id: int):
        collaborator = CollaboratorModel.find_by_id_or_404(collaborator_id)
        return collaborator_schema.dump(collaborator), 200

    @doc(description="My First GET Awesome API.", tags=["Awesome"])
    @use_kwargs(collaborator_schema, location=("json"))
    @marshal_with(collaborator_schema, apply=False)
    def post(self, *args, **kwargs):
        collaborator_json = request.get_json()
        collaborator = collaborator_schema.load(collaborator_json)

        user = UserModel.find_by_id_or_404(collaborator.user_id)
        if user.collaborator:
            return {
                "message": gettext("user_already_collaborator").format(user.id)
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


class CollaboratorAudio(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        collaborator = user.collaborator
        if not collaborator:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404

        subtask = collaborator.current_subtask
        if not subtask:
            return {"message": gettext("collaborator_subtask_not_found")}, 404

        audio_file = subtask.audio_file
        if audio_file:
            return {
                "message": gettext("subtask_has_audio_file").format(audio_file)
            }, 400

        subtask.audio_file = str(uuid4())
        subtask.save_to_db()

        return subtask_schema.dump(subtask), 200
