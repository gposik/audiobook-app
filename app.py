import os

from flask import Flask, send_file
from flask_restful import Api
from flask_uploads import configure_uploads
from flask_jwt_extended import JWTManager
from werkzeug.security import safe_join
from flask_apispec.extension import FlaskApiSpec

from ma import ma
from db import db
from config import env_config
from blacklist import BLACKLIST
from errors import error_bp
from libs.file_helper import AUDIO_CONF, IMAGE_CONF, BOOK_CONF, FileHelper
from resources.audio import AudioUpload
from resources.collaborator import (
    Collaborator,
    CollaboratorAudio,
    CollaboratorHistory,
    CollaboratorList,
    CollaboratorSubtask,
)
from resources.subtask import TaskSubtask, TaskSubtaskList
from resources.task import Task, TaskList
from resources.user import User, UserLogin, UserRegister, UserLogout, TokenRefresh
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.audiobook import Audiobook, AudiobookList
from resources.book import BookUpload, Book

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object(env_config["development"])

configure_uploads(
    app, (FileHelper(*IMAGE_CONF), FileHelper(*BOOK_CONF), FileHelper(*AUDIO_CONF))
)
app.register_blueprint(error_bp)

api = Api(app)
docs = FlaskApiSpec(app)


@api.representation("application/octet-stream")
def output_file(data, code, headers):
    filepath = safe_join(data["directory"], data["filename"])

    response = send_file(
        path_or_file=filepath,
        mimetype="application/octet-stream",
        as_attachment=True,
        attachment_filename=data["filename"],
    )
    return response


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


api.add_resource(User, "/users/<int:user_id>")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/user-confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(CollaboratorList, "/collaborators")
api.add_resource(Collaborator, "/collaborator/<int:collaborator_id>", "/collaborator")
api.add_resource(
    CollaboratorSubtask,
    "/collaborator/<int:collaborator_id>/subtask",
    "/collaborator/<int:collaborator_id>/subtask/<int:subtask_id>",
)
api.add_resource(CollaboratorAudio, "/collaborator/subtask/audio")
api.add_resource(CollaboratorHistory, "/collaborator/<int:collaborator_id>/history")
api.add_resource(Audiobook, "/audiobook/<int:audiobook_id>", "/audiobook")
api.add_resource(AudiobookList, "/audiobooks")
api.add_resource(Task, "/task/<int:task_id>", "/task")
api.add_resource(TaskList, "/tasks")
api.add_resource(
    TaskSubtask,
    "/task/<int:task_id>/subtask/<int:subtask_id>",
    "/task/<int:task_id>/subtask",
)
api.add_resource(TaskSubtaskList, "/task/<int:task_id>/subtasks")
api.add_resource(BookUpload, "/upload/book")
api.add_resource(Book, "/book/<string:filename>")
api.add_resource(AudioUpload, "/upload/audio")


docs.register(Collaborator)

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000)
