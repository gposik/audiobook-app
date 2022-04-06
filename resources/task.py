from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from config import ALREADY_EXISTS, CREATED_SUCCESSFULLY, NOT_FOUND
from models.task import TaskModel
from schemas.task import TaskSchema

RESOURCE_NAME = "Task"

task_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)


class Task(Resource):
    @classmethod
    def get(cls, task_id: int):
        task = TaskModel.find_by_id(task_id)
        if not task:
            return {"message": NOT_FOUND.format(RESOURCE_NAME)}, 404
        return task_schema.dump(task), 200

    @classmethod
    def post(cls):
        task_json = request.get_json()
        task = task_schema.load(task_json)

        if TaskModel.find_by_audiobook_id(task.audiobook_id):
            return {
                "message": ALREADY_EXISTS.format(RESOURCE_NAME, "audiobook_id")
            }, 400

        task.save_to_db()

        return {
            "message": CREATED_SUCCESSFULLY.format(RESOURCE_NAME),
            "task": task_schema.dump(task),
        }, 201


class TaskList(Resource):
    @classmethod
    def get(cls):
        return {"tasks": task_list_schema.dump(TaskModel.find_all())}, 200
