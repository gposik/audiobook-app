import mobi
import html2text
import os

from io import StringIO
from flask_restful import Resource
from flask import current_app as app, request
from flask_jwt_extended import jwt_required
from config import ALREADY_EXISTS, CREATED_SUCCESSFULLY, NOT_FOUND
from models.audiobook import AudiobookModel
from models.subtask import SubtaskModel
from models.task import TaskModel
from schemas.task import TaskSchema

RESOURCE_NAME = "Task"

task_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)


def get_text_from_mobi_file(file_path):
    tempdir, filepath = mobi.extract(file_path)
    with open(filepath, "r") as file:
        content = file.read()
    return html2text.html2text(content)


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

        if not AudiobookModel.find_by_id(task.audiobook_id):
            return {"message": "The audiobook_id entered does not exists"}, 400

        if TaskModel.find_by_audiobook_id(task.audiobook_id):
            return {
                "message": ALREADY_EXISTS.format(RESOURCE_NAME, "audiobook_id")
            }, 400

        task.save_to_db()

        # Ordenar los fragmentos
        sorted_fragments = sorted(task.fragments, key=lambda i: i["first_line"])

        # Obtener filepath
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], task.audiobook.book_file)

        # Obtener texto de archivo .mobi
        text = get_text_from_mobi_file(file_path)

        # Iterar sobre los rangos para obter los fragmentos e instanciar las subtaks
        iter_text = StringIO(text)
        last = 0
        for fragment in sorted_fragments:
            init = fragment["first_line"]
            finish = fragment["last_line"]

            for _ in range(last, init):
                next(iter_text)

            frg = ""
            for _ in range(init, finish + 1):
                frg += iter_text.readline()

            last = finish

            subtask = SubtaskModel(fragment=frg, task_id=task.id)
            subtask.save_to_db()

        return {
            "message": CREATED_SUCCESSFULLY.format(RESOURCE_NAME),
            "task": task_schema.dump(task),
        }, 201


class TaskList(Resource):
    @classmethod
    def get(cls):
        return {"tasks": task_list_schema.dump(TaskModel.find_all())}, 200
