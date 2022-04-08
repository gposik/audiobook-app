from ma import ma
from models.subtask import SubtaskModel


class SubtaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SubtaskModel
        dump_only = ("id",)
        load_only = ("task_id",)
        include_fk = True
        load_instance = True
