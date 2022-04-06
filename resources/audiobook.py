from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from models.audiobook import AudiobookModel
from schemas.audiobook import AudiobookSchema
from config import *

RESOURCE_NAME = "Audiobook"

audiobook_schema = AudiobookSchema()
audiobooks_schema = AudiobookSchema(many=True)


class Audiobook(Resource):
    @classmethod
    def get(cls, audiobook_id: int):
        audiobook = AudiobookModel.find_by_id(audiobook_id)
        if not audiobook:
            return {"message": NOT_FOUND.format(RESOURCE_NAME)}, 404
        return audiobook_schema.dump(audiobook), 200

    @classmethod
    def post(cls):
        audiobook_json = request.get_json()
        audiobook = audiobook_schema.load(audiobook_json)

        if AudiobookModel.find_by_name(audiobook.name):
            return {"message": ALREADY_EXISTS.format(RESOURCE_NAME, "name")}, 400

        audiobook.save_to_db()

        return {
            "message": CREATED_SUCCESSFULLY.format(RESOURCE_NAME),
            "audiobook": audiobook_schema.dump(audiobook),
        }, 201


class AudiobookList(Resource):
    @classmethod
    def get(cls):
        return {"audiobooks": audiobooks_schema.dump(AudiobookModel.find_all())}, 200
