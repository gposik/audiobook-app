from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from config import CREATED_SUCCESSFULLY, NOT_FOUND
from models.subtask import SubtaskModel
from schemas.subtask import SubtaskSchema

RESOURCE_NAME = "Subtask"

subtask_schema = SubtaskSchema()


class TaskSubtask(Resource):
    @classmethod
    def get(cls, task_id, subtask_id):
        subtask = SubtaskModel.find_by_task_id(task_id, subtask_id)
        if not subtask:
            return {"message": NOT_FOUND.format(RESOURCE_NAME)}, 404
        return subtask_schema.dump(subtask), 200

    @classmethod
    def post(cls, task_id):
        subtask_json = request.get_json()
        subtask = subtask_schema.load(subtask_json)
        subtask.task_id = task_id

        subtask.save_to_db()

        return {
            "message": CREATED_SUCCESSFULLY.format(RESOURCE_NAME),
            "data": subtask_schema.dump(subtask),
        }, 201
