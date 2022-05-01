from ma import ma
from models.task import TaskModel
from schemas.subtask import SubtaskSchema

from marshmallow import (
    ValidationError,
    fields,
    Schema,
    validate,
    validates,
    validates_schema,
)


def range_including_end(start, end):
    return range(start, end + 1)


def is_positive(value):
    return value > 0


class FragmentSchema(Schema):
    first_line = fields.Int(
        required=True, validate=validate.And(validate.Range(min=0), is_positive)
    )
    last_line = fields.Int(required=True, validate=validate.Range(min=0))

    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["first_line"] >= data["last_line"]:
            raise ValidationError("last_line must be greater than first_line")


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True

    subtasks = ma.Nested(SubtaskSchema, many=True)
    fragments = fields.List(
        fields.Nested(FragmentSchema()),
        required=True,
        load_only=True,
        validate=validate.Length(min=1),
    )

    @validates("fragments")
    def validate_fragments(self, fragments):
        ranges = []
        for fragment in fragments:
            try:
                a = int(fragment["first_line"])
                b = int(fragment["last_line"])
            except ValueError:
                print("Lines should be integer.")
            for r in ranges:
                if a in r or b in r:
                    raise ValidationError(
                        {
                            "fragment": fragment,
                            "error": "range cannot be included in another range",
                        }
                    )
            ranges.append(list(range_including_end(a, b)))


# class TaskSchema2(Schema):
#     id = fields.Int(dump_only=True)
#     collaborators_number = fields.Int(required=True)
#     is_completed = fields.Boolean(required=False)
#     audiobook_id = fields.Int(required=True)
#     subtasks = fields.List(fields.Nested(SubtaskSchema))
#     fragments = fields.List(
#         fields.Nested(FragmentSchema()),
#         required=True,
#         load_only=True,
#         validate=validate.Length(min=1),
#     )

#     @validates("fragments")
#     def validate_fragments(self, fragments):
#         ranges = []
#         for fragment in fragments:
#             a = fragment["first_line"]
#             b = fragment["last_line"]
#             for r in ranges:
#                 if a in r or b in r:
#                     raise ValidationError(
#                         {
#                             "fragment": fragment,
#                             "error": "range cannot be included in another range",
#                         }
#                     )
#             ranges.append(list(range1(a, b)))

#     @post_load
#     def make_task(self, data, **kwargs):
#         return TaskModel(**data)
