import os
from flask_restful import Resource
from models.task import TaskModel
from utils.string_utils import to_snake_case
from libs.audio_builder import concatenate_sounds, FORMAT
from libs.file_helper import AUDIO_CONF, FileHelper

file_helper = FileHelper(*AUDIO_CONF)


class MakeTask(Resource):
    @classmethod
    def get(cls):
        # 1. Get tasks to be finished
        tasks = TaskModel.get_tasks_to_be_finished()

        # 2. For each task iterate over each "task_id" directory
        for task in tasks:
            task_folder = f"task_{task.id}"
            # 3. Iterate over each "subtask_id" directory getting the audio files paths
            audio_paths = []
            for subtask in task.subtasks:
                subtask_folder = os.path.join(task_folder, f"subtask_{subtask.id}")
                audio_path = file_helper.find_file_any_format(
                    subtask.audio_file, subtask_folder
                )
                if audio_path:
                    audio_paths.append(audio_path)

            # 4. For each audio_path, cut leading silence (add a second of silence at the end), merge with task_sound
            unified_sound = concatenate_sounds(audio_paths)

            # 5. Export audio in audiobook_id directory
            audiobook = task.audiobook
            filename = "{}.{}".format(to_snake_case(audiobook.name), FORMAT)
            audiobook_folder = os.path.join(
                file_helper.destination, f"audiobook_{audiobook.id}"
            )
            if not os.path.exists(audiobook_folder):
                os.makedirs(audiobook_folder)
            audiobook_path = os.path.join(audiobook_folder, filename)

            unified_sound.export(audiobook_path, format=FORMAT)

            audiobook.audio_file = audiobook_path
            audiobook.save_to_db()

        return {"message": "Success!"}, 201
