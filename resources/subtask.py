from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from config import CREATED_SUCCESSFULLY, NOT_FOUND
from models.subtask import SubtaskModel
from models.task import TaskModel
from schemas.subtask import SubtaskSchema

RESOURCE_NAME = "Subtask"

subtask_schema = SubtaskSchema()
subtask_list_schema = SubtaskSchema(many=True)


class TaskSubtask(Resource):
    @classmethod
    def get(cls, task_id, subtask_id):
        task = TaskModel.find_by_id(task_id)
        if not task:
            return {"message": NOT_FOUND.format("Task")}, 404

        subtask = task.get_subtask_by_id(subtask_id)
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


class TaskSubtaskList(Resource):
    @classmethod
    def get(cls, task_id):
        task = TaskModel.find_by_id(task_id)
        if not task:
            return {"message": NOT_FOUND.format("Task")}, 404
        return {"data": subtask_list_schema.dump(task.subtasks)}
