import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from ma import ma
from db import db
from config import env_config
from blacklist import BLACKLIST
from errors import error_bp
from resources.subtask import TaskSubtask, TaskSubtaskList
from resources.task import Task, TaskList
from resources.user import (
    User,
    UserLogin,
    UserRegister,
    UserLogout,
    TokenRefresh,
    UserSubtask,
)
from resources.audiobook import Audiobook, AudiobookList
from resources.file import File

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object(env_config["development"])

app.register_blueprint(error_bp)

api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


api.add_resource(User, "/users/<int:user_id>")
api.add_resource(
    UserSubtask,
    "/user/<int:user_id>/subtask",
    "/user/<int:user_id>/subtask/<int:subtask_id>",
)
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
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
