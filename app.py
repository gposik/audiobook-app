import os
from flask import Flask, send_file
from flask_restful import Api
from flask_jwt_extended import JWTManager
from werkzeug.security import safe_join

from ma import ma
from db import db
from config import env_config
from blacklist import BLACKLIST
from errors import error_bp
from resources.collaborator import Collaborator, CollaboratorList, CollaboratorSubtask
from resources.subtask import TaskSubtask, TaskSubtaskList
from resources.task import Task, TaskList
from resources.user import (
    User,
    UserLogin,
    UserRegister,
    UserLogout,
    TokenRefresh,
    UserConfirm,
)
from resources.audiobook import Audiobook, AudiobookList
from resources.file import File

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object(env_config["development"])

app.register_blueprint(error_bp)

api = Api(app)


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
api.add_resource(UserConfirm, "/user-confirm/<int:user_id>")
api.add_resource(CollaboratorList, "/collaborators")
api.add_resource(Collaborator, "/collaborator/<int:collaborator_id>", "/collaborator")
api.add_resource(
    CollaboratorSubtask,
    "/collaborator/<int:collaborator_id>/subtask",
    "/collaborator/<int:collaborator_id>/subtask/<int:subtask_id>",
)
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
api.add_resource(File, "/upload-file", "/download-file")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
