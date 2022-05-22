from re import S
import mobi
import html2text
import os

from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from libs.file_helper import BOOK_CONF, FileHelper
from libs.strings import gettext
from models.audiobook import AudiobookModel
from models.subtask import SubtaskModel
from models.task import TaskModel
from schemas.task import TaskSchema

RESOURCE_NAME = "Task"

task_schema = TaskSchema()
task_list_schema = TaskSchema(many=True)

file_helper = FileHelper(*BOOK_CONF)


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

        filename = task.audiobook.book_file
        filepath = file_helper.find_file_any_format(filename=filename)
        try:
            book_text = get_text_from_mobi_file(filepath)
        except FileNotFoundError:
            task.delete_from_db()
            return {"message": gettext("book_not_found").format(filename)}, 404

        fragments = task.get_fragments_from_text(book_text)
        print(fragments)

        for fragment in fragments:
            subtask = SubtaskModel(fragment=fragment, task_id=task.id)
            subtask.save_to_db()

        return {
            "message": gettext("entity_created").format(RESOURCE_NAME),
            "task": task_schema.dump(task),
        }, 201


class TaskList(Resource):
    @classmethod
    def get(cls):
        return {"tasks": task_list_schema.dump(TaskModel.find_all())}, 200
