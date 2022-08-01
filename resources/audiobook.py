import uuid
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from libs.strings import gettext
from models.audiobook import AudiobookModel
from schemas.audiobook import AudiobookSchema


RESOURCE_NAME = "Audiobook"

audiobook_schema = AudiobookSchema()
audiobooks_schema = AudiobookSchema(many=True)


class Audiobook(Resource):
    @classmethod
    def get(cls, audiobook_id: int):
        audiobook = AudiobookModel.find_by_id(audiobook_id)
        if not audiobook:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404
        return audiobook_schema.dump(audiobook), 200

    @classmethod
    def post(cls):
        audiobook_json = request.get_json()
        audiobook = audiobook_schema.load(audiobook_json)

        if AudiobookModel.find_by_name(audiobook.name):
            return {
                "message": gettext("entity_with_already_exists").format(
                    RESOURCE_NAME, "name"
                )
            }, 400

        audiobook.book_file = str(uuid.uuid4())

        audiobook.save_to_db()

        return {
            "message": gettext("entity_created").format(RESOURCE_NAME),
            "audiobook": audiobook_schema.dump(audiobook),
        }, 201

    @classmethod
    def put(cls, audiobook_id: int):
        audiobook = AudiobookModel.find_by_id(audiobook_id)
        audiobook_json = request.get_json()
        new_audiobook = audiobook_schema.load(audiobook_json)

        if audiobook:
            audiobook.name = new_audiobook.name
            audiobook.author = new_audiobook.author
            response = {"message": "entity_updated", "code": 200}
        else:
            audiobook = new_audiobook
            audiobook.book_file = str(uuid.uuid4())
            response = {"message": "entity_created", "code": 201}

        audiobook.save_to_db()

        return {
            "message": gettext(response["message"]).format(RESOURCE_NAME),
            "audiobook": audiobook_schema.dump(audiobook),
        }, response["code"]

    @classmethod
    def delete(cls, audiobook_id: int):
        audiobook = AudiobookModel.find_by_id(audiobook_id)
        if not audiobook:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404

        audiobook.delete_from_db()
        return {"message": gettext("entity_deleted").format(RESOURCE_NAME)}, 204


class AudiobookList(Resource):
    @classmethod
    def get(cls):
        return {"audiobooks": audiobooks_schema.dump(AudiobookModel.find_all())}, 200
