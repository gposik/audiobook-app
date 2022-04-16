from marshmallow import fields, Schema, INCLUDE
from marshmallow.validate import Length


class FileQuerySchema(Schema):
    class Meta:
        unknown = INCLUDE

    name = fields.Str(required=True, validate=Length(max=50))
    preview = fields.Boolean(required=False)


class FileSchema(Schema):
    file = fields.Raw(required=True, type="file")
