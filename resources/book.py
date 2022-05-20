import traceback
import os

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.file_helper import FileHelper
from libs.strings import gettext
from schemas.book import BookQuerySchema, BookSchema

book_schema = BookSchema()
book_query_schema = BookQuerySchema()

file_helper = FileHelper("book")


class BookUpload(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        """
        This endpoint is used to upload a book file. It uses the
        JWT to retrieve user information and save the book in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.mobi to filename_1.pdf).
        """
        query_params = book_query_schema.load(request.args)
        name = query_params["name"]

        data = book_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        extension = file_helper.get_extension(data["book"])
        try:
            book_path = file_helper.save_file(
                data["book"], folder=folder, name=(name + extension)
            )
            # here we only return the basename of the book and hide the internal folder structure from our user
            basename = file_helper.get_basename(book_path)
            return {"message": gettext("book_uploaded").format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            return {"message": gettext("book_illegal_extension").format(extension)}, 400
