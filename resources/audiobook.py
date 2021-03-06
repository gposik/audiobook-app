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

        last_audiobook = AudiobookModel.query.order_by(text("id desc")).first()
        if last_audiobook:
            new_id = last_audiobook.id + 1
        else:
            new_id = 1

        audiobook.book_file = f"{new_id}-{str(uuid.uuid4())}"

        audiobook.save_to_db()

        return {
            "message": gettext("entity_created").format(RESOURCE_NAME),
            "audiobook": audiobook_schema.dump(audiobook),
        }, 201

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
