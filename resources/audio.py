import traceback
import os

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

        user_id = get_jwt_identity()
        user = UserModel.find_by_id_or_404(user_id)

        collaborator = user.collaborator
        if not collaborator:
            return {"message": gettext("user_not_collaborator").format(user.id)}, 400

        subtask = collaborator.current_subtask
        if not subtask:
            return {"message": gettext("collaborator_subtask_not_found")}, 404

        task = subtask.task

        folder = os.path.join(f"task_{task.id}", f"subtask_{subtask.id}")

        data = audio_schema.load(request.files)
        extension = file_helper.get_extension(data["audio"])

        try:
            # files_in_folder = file_helper.get_files(folder=folder)
            # current_file = next(iter(files_in_folder), None)

            audio_path = file_helper.save(
                data["audio"], folder=folder, name=(name + extension)
            )

            basename = file_helper.get_basename(audio_path)
            message = {
                "message": gettext("file_uploaded").format(RESOURCE_NAME, basename)
            }
        except UploadNotAllowed as e:
            print(e.messages)
            return {"message": gettext("file_illegal_extension").format(extension)}, 400
        except:
            traceback.print_exc()
            return {"message": gettext("file_upload_failed")}, 500
        else:
            pass
            # if current_file:
            #     file_helper.remove_file(file=current_file, folder=folder)

        return message, 201


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
