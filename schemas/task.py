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


def is_positive(value: int):
    if value <= 0:
        raise ValidationError("Value should be greater than zero.")
    return value > 0


class FragmentSchema(Schema):
    first_line = fields.Int(required=True, validate=is_positive)
    last_line = fields.Int(required=True, validate=is_positive)

    @validates_schema
    def validate_numbers(self, data: dict, **kwargs):
        if data["first_line"] >= data["last_line"]:
            raise ValidationError("last_line must be greater than first_line")


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True

    subtasks = ma.Nested(SubtaskSchema, many=True, only=("id",))
    fragments = fields.List(
        fields.Nested(FragmentSchema()),
        required=True,
        load_only=True,
        validate=validate.Length(min=1),
    )

    @validates("fragments")
    def validate_fragments(self, fragments: list):
        fragments_schema = FragmentSchema(many=True)
        valid_fragments = fragments_schema.load(fragments)

        ranges = []
        for fragment in valid_fragments:
            first_line = fragment["first_line"]
            last_line = fragment["last_line"]
            for rnge in ranges:
                if first_line in rnge or last_line in rnge:
                    raise ValidationError(
                        {
                            "fragment": fragment,
                            "error": "The range cannot be included in another range.",
                        }
                    )
            ranges.append(list(range(first_line, last_line + 1)))
