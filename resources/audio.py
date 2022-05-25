import traceback
import os
from uuid import uuid4

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.file_helper import FileHelper, AUDIO_CONF
from libs.strings import gettext
from models.user import UserModel
from schemas.audio import AudioQuerySchema, AudioSchema

RESOURCE_NAME = "Audio"

audio_schema = AudioSchema()
audio_query_schema = AudioQuerySchema()

file_helper = FileHelper(*AUDIO_CONF)


class AudioUpload(Resource):
    @jwt_required()
    def post(self):

        query_params = audio_query_schema.load(request.args)
        name = query_params["name"]

        # user
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        folder = f"user_{user_id}"
        collaborator = user.collaborator
        if collaborator:
            subtask = collaborator.current_subtask
            task = subtask.task
            folder = os.path.join(folder, f"task_{task.id}", f"subtask_{subtask.id}")

        data = audio_schema.load(request.files)
        extension = file_helper.get_extension(data["audio"])
        try:
            audio_path = file_helper.save(
                data["audio"], folder=folder, name=(name + extension)
            )
            basename = file_helper.get_basename(audio_path)
            return {
                "message": gettext("file_uploaded").format(RESOURCE_NAME, basename)
            }, 201
        except UploadNotAllowed:
            return {"message": gettext("file_illegal_extension").format(extension)}, 400


# class Audio(Resource):
#     @classmethod
#     def get(cls, filename: str):
#         """
#         This endpoint returns the requested audio if exists.
#         """
#         # check if filename is URL secure
#         if not file_helper.is_filename_safe(filename):
#             return {"message": gettext("file_illegal_filename").format(filename)}, 400
#         try:
#             # try to send the requested file to the user with status code 200
#             return send_file(file_helper.path(filename))
#         except FileNotFoundError:
#             return {
#                 "message": gettext("file_not_found").format(RESOURCE_NAME, filename)
#             }, 404

#     @classmethod
#     def delete(cls, filename: str):
#         """
#         This endpoint is used to delete the requested audio under the audios folder.
#         """

#         # check if filename is URL secure
#         if not file_helper.is_filename_safe(filename):
#             return {"message": gettext("file_illegal_filename").format(filename)}, 400

#         try:
#             os.remove(file_helper.path(filename))
#             return {
#                 "message": gettext("file_deleted").format(RESOURCE_NAME, filename)
#             }, 200
#         except FileNotFoundError:
#             return {
#                 "message": gettext("file_not_found").format(RESOURCE_NAME, filename)
#             }, 404
#         except:
#             traceback.print_exc()
#             return {"message": gettext("file_delete_failed")}, 500
