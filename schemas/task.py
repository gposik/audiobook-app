from libs.strings import gettext
from ma import ma
from models.task import TaskModel
from schemas.subtask import SubtaskSchema

from marshmallow import (
    ValidationError,
    fields,
    Schema,
    pre_load,
    validate,
    validates,
    validates_schema,
)


def is_positive(value: int):
    if value <= 0:
        raise ValidationError("Value should be greater than zero.")
    return value > 0


class FragmentRangeSchema(Schema):
    first_line = fields.Int(required=True, validate=is_positive)
    last_line = fields.Int(required=True, validate=is_positive)

    @validates_schema
    def validate_numbers(self, data: dict, **kwargs):
        if data["first_line"] >= data["last_line"]:
            raise ValidationError("last_line must be greater than first_line")


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskModel
        dump_only = ("id", "is_completed")
        include_fk = True
        load_instance = True

    subtasks = ma.Nested(SubtaskSchema, many=True, only=("id",))
    fragments_ranges = fields.List(
        fields.Nested(FragmentRangeSchema()),
        required=True,
        load_only=True,
        validate=validate.Length(min=1),
    )
    is_completed = fields.Boolean()

    @validates("fragments_ranges")
    def validate_fragments_ranges(self, fragments_ranges: list):
        FragmentRangeSchema(many=True).load(fragments_ranges)

        ranges = []
        for fragment_range in fragments_ranges:
            first_line = fragment_range["first_line"]
            last_line = fragment_range["last_line"]
            for rnge in ranges:
                if first_line in rnge or last_line in rnge:
                    raise ValidationError(
                        {
                            "fragment_range": fragment_range,
                            "error": gettext("task_invalid_fragment_range"),
                        }
                    )
            ranges.append(list(range(first_line, last_line + 1)))

    @pre_load
    def sort_fragments_ranges(self, data, **kwargs):
        sorted_fragments_ranges = sorted(
            data["fragments_ranges"], key=lambda i: i["first_line"]
        )
        data["fragments_ranges"] = sorted_fragments_ranges
        return data
