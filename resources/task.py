import mobi
import html2text
import os

from io import StringIO
from flask_restful import Resource
from flask import current_app as app, request
from flask_jwt_extended import jwt_required
from libs.strings import gettext
from models.audiobook import AudiobookModel
from models.subtask import SubtaskModel
from models.task import TaskModel
from schemas.task import TaskSchema

RESOURCE_NAME = "Task"

task_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)


def get_text_from_mobi_file(file_path: str):
    tempdir, filepath = mobi.extract(file_path)
    with open(filepath, "r") as file:
        content = file.read()
    return html2text.html2text(content)


class Task(Resource):
    @classmethod
    def get(cls, task_id: int):
        task = TaskModel.find_by_id(task_id)
        if not task:
            return {"message": gettext("entity_not_found").format(RESOURCE_NAME)}, 404
        return task_schema.dump(task), 200

    @classmethod
    def post(cls):
        task_json = request.get_json()
        task = task_schema.load(task_json)

        if not AudiobookModel.find_by_id(task.audiobook_id):
            return {"message": gettext("entity_not_found").format("Audiobook")}, 404

        if TaskModel.find_by_audiobook_id(task.audiobook_id):
            return {
                "message": gettext("entity_with_already_exists").format(
                    RESOURCE_NAME, "audiobook_id"
                )
            }, 400

        task.save_to_db()

        # Obtain filepath
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], task.audiobook.book_file)
        # Obtain text from .mobi file
        try:
            book_text = get_text_from_mobi_file(file_path)
        except FileNotFoundError:
            task.delete_from_db()
            return {"message": gettext("entity_not_found").format("File")}, 404

        # Ordenar los fragmentos
        sorted_fragments = sorted(task.fragments, key=lambda i: i["first_line"])
        # Iterar sobre los rangos, obtener los fragmentos e instanciar las subtaks
        book_iter = StringIO(book_text)
        last = 0
        for fragment in sorted_fragments:
            init = fragment["first_line"]
            finish = fragment["last_line"]

            for _ in range(last, init):
                next(book_iter)

            frg = ""
            for _ in range(init, finish + 1):
                frg += book_iter.readline()

            last = finish

            subtask = SubtaskModel(fragment=frg, task_id=task.id)
            subtask.save_to_db()

        return {
            "message": gettext("entity_created").format(RESOURCE_NAME),
            "task": task_schema.dump(task),
        }, 201


class TaskList(Resource):
    @classmethod
    def get(cls):
        return {"tasks": task_list_schema.dump(TaskModel.find_all())}, 200
