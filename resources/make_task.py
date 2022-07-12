import os
from pydub import AudioSegment
from flask_restful import Resource
from libs.audio_builder import detect_leading_silence
from libs.file_helper import AUDIO_CONF, FileHelper
from models.task import TaskModel

file_helper = FileHelper(*AUDIO_CONF)


class MakeTask(Resource):
    @classmethod
    def get(cls):
        # 1. Get tasks to be finished
        tasks = TaskModel.get_to_be_finished_tasks()
        print(tasks)

        # 2. For each task iterate over each "task_id" directory
        for task in tasks:
            print("entré")
            task_folder = f"task_{task.id}"
            # 3. Iterate over each "subtask_id" directory getting the audio files paths
            audio_paths = []
            # for subtask in task.subtasks:
            #     subtask_folder = os.path.join(task_folder, f"subtask_{subtask.id}")
            #     audio_path = file_helper.find_file_any_format(
            #         subtask.audio_file, subtask_folder
            #     )
            #     audio_paths.append(audio_path)

            # # 4. For each audio_path, cut leading silence (add a second of silence at the end), merge with task_sound
            # merged_sound = ""
            # for path in audio_paths:
            #     sound = AudioSegment.from_file(path, format="ogg")
            #     start_trim = detect_leading_silence(sound)
            #     end_trim = detect_leading_silence(sound.reverse())
            #     duration = len(sound)
            #     trimmed_sound = sound[start_trim : duration - end_trim]

            #     merged_sound += trimmed_sound

            # # 5. Export audio in task_id directory
            # audiobook_path = os.path.join(task_folder, task.audiobook.audio_file)
            # merged_sound.export(audiobook_path, format="ogg")

        return {"message": "Success!"}, 201
