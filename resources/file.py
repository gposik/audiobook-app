import os

from flask_restful import Resource
from flask import current_app, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from schemas.file import FileQuerySchema, FileSchema

file_query_schema = FileQuerySchema()
file_schema = FileSchema()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def mimetype_check_passes(uploaded_file):
    mimetype = uploaded_file.content_type
    return mimetype in current_app.config["ALLOWED_MIMETYPES_EXTENSIONS"]


class File(Resource):
    @classmethod
    def post(cls):
        query_params = file_query_schema.load(request.args)
        name = query_params["name"]

        uploaded_files = file_schema.load(request.files)
        uploaded_file = uploaded_files.get("file")

        if isinstance(uploaded_file, FileStorage) and allowed_file(
            uploaded_file.filename
        ):
            # Make the filename safe, remove unsupported chars
            uploaded_file.filename = secure_filename(name)

            target = os.path.join(
                current_app.config["UPLOAD_FOLDER"], uploaded_file.filename
            )

            uploaded_file.save(target)
            return ({"message": "File uploaded successfully"}), 201

        return ({"message": "An error occured"}), 400

    @classmethod
    def get(cls):
        query_params = file_query_schema.load(request.args)
        name = query_params["name"]
        pass
