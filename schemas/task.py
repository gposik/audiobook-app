from ma import ma
from models.task import TaskModel


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
