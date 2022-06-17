import traceback
import os

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request

from libs.file_helper import FileHelper, BOOK_CONF
from libs.strings import gettext
from schemas.book import BookQuerySchema, BookSchema

book_schema = BookSchema()
book_query_schema = BookQuerySchema()

file_helper = FileHelper(*BOOK_CONF)


class BookUpload(Resource):
    @classmethod
    def post(cls):
        """
        This endpoint is used to upload a book file.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.mobi to filename_1.pdf).
        """
        query_params = book_query_schema.load(request.args)
        name = query_params["name"]

        data = book_schema.load(request.files)
        extension = file_helper.get_extension(data["book"])
        try:
            book_path = file_helper.save(data["book"], name=(name + extension))
            # here we only return the basename of the book and hide the internal folder structure from our user
            basename = file_helper.get_basename(book_path)
            return {"message": gettext("book_uploaded").format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            return {"message": gettext("file_illegal_extension").format(extension)}, 400


class Book(Resource):
    @classmethod
    def get(cls, filename: str):
        """
        This endpoint returns the requested book if exists.
        """
        # check if filename is URL secure
        if not file_helper.is_filename_safe(filename):
            return {"message": gettext("file_illegal_filename").format(filename)}, 400
        try:
            # try to send the requested file to the user with status code 200
            return send_file(file_helper.path(filename))
        except FileNotFoundError:
            return {"message": gettext("book_not_found").format(filename)}, 404

    @classmethod
    def delete(cls, filename: str):
        """
        This endpoint is used to delete the requested book under the books folder.
        """

        # check if filename is URL secure
        if not file_helper.is_filename_safe(filename):
            return {"message": gettext("file_illegal_filename").format(filename)}, 400

        try:
            os.remove(file_helper.path(filename))
            return {"message": gettext("book_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("book_not_found").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("book_delete_failed")}, 500


# class AvatarUpload(Resource):
#     @jwt_required
#     def put(self):
#         """
#         This endpoint is used to upload user avatar. All avatars are named after the user's id
#         in such format: user_{id}.{ext}.
#         It will overwrite the existing avatar.
#         """
#         data = image_schema.load(request.files)
#         filename = f"user_{get_jwt_identity()}"
#         folder = "avatars"
#         avatar_path = file_helper.find_image_any_format(filename, folder)
#         if avatar_path:
#             try:
#                 os.remove(avatar_path)
#             except:
#                 return {"message": gettext("avatar_delete_failed")}, 500

#         try:
#             ext = file_helper.get_extension(data["image"].filename)
#             avatar = filename + ext  # use our naming format + true extension
#             avatar_path = file_helper.save_file(
#                 data["image"], folder=folder, name=avatar
#             )
#             basename = file_helper.get_basename(avatar_path)
#             return {"message": gettext("avatar_uploaded").format(basename)}, 200
#         except UploadNotAllowed:  # forbidden file type
#             extension = file_helper.get_extension(data["image"])
#             return {"message": gettext("image_illegal_extension").format(extension)}, 400


# class Avatar(Resource):
#     @classmethod
#     def get(cls, user_id: int):
#         """
#         This endpoint returns the avatar of the user specified by user_id.
#         """
#         folder = "avatars"
#         filename = f"user_{user_id}"
#         avatar = file_helper.find_image_any_format(filename, folder)
#         if avatar:
#             return send_file(avatar)
#         return {"message": gettext("avatar_not_found")}, 404
