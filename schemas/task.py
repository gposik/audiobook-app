from ma import ma
from models.task import TaskModel
from schemas.subtask import SubtaskSchema


class TaskSchema(ma.SQLAlchemyAutoSchema):
    subtasks = ma.Nested(SubtaskSchema, many=True)

    class Meta:
        model = TaskModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
