from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from operator import itemgetter
from utils.api_utils import request_schemas_load
from libs.strings import gettext
from models.subtask import SubtaskModel
from models.task import TaskModel
from schemas.subtask import SubtaskQuerySchema, SubtaskSchema

RESOURCE_NAME = "Subtask"

subtask_schema = SubtaskSchema()
subtask_list_schema = SubtaskSchema(many=True)


class TaskSubtask(Resource):
    @classmethod
    def get(cls, task_id: int, subtask_id: int):
        task = TaskModel.find_by_id(task_id)
        if not task:
            return {"message": gettext("entity_not_found").format("Task")}, 404

        subtask = task.get_subtask_by_id(subtask_id)
        if not subtask:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404

        return subtask_schema.dump(subtask), 200

    @classmethod
    def patch(cls, task_id: int, subtask_id: int):
        results = request_schemas_load(
            SubtaskSchema(
                partial=True,
                load_instance=False,
                only=(
                    "fragment",
                    "is_completed",
                ),
            )
        )
        body = itemgetter("body")(results)

        if not TaskModel.find_by_id_or_404(task_id):
            return {"message": gettext("entity_not_found").format("Task")}, 404

        subtask = SubtaskModel.find_by_id_or_404(subtask_id)
        if not subtask:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404

        for key, value in body.items():
            if getattr(subtask, key) is not None:
                setattr(subtask, key, value)

        subtask.save_to_db()

        return subtask_schema.dump(subtask), 200

    @classmethod
    def post(cls, task_id: int):
        subtask_json = request.get_json()
        subtask = subtask_schema.load(subtask_json)
        subtask.task_id = task_id

        subtask.save_to_db()

        return {
            "message": gettext("entity_created").format(RESOURCE_NAME),
            "data": subtask_schema.dump(subtask),
        }, 201


class TaskSubtaskList(Resource):
    @classmethod
    def get(cls, task_id: int):
        task = TaskModel.find_by_id_or_404(task_id)

        results = request_schemas_load(SubtaskQuerySchema())
        query = itemgetter("query")(results)

        data = task.subtasks

        if "is_completed" in query:
            data = [x for x in data if x.is_completed == query["is_completed"]]
        if "is_expired" in query:
            data = [x for x in data if x.is_expired == query["is_expired"]]
        if "id" in query:
            data = [x for x in data if x.id == query["id"]]

        return {"data": subtask_list_schema.dump(data)}
