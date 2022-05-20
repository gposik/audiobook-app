from werkzeug.datastructures import FileStorage
from marshmallow import Schema, fields, INCLUDE
from marshmallow.validate import Length


class FileStorageField(fields.Field):
    default_error_messages = {"invalid": "Not a valid file."}

    def _deserialize(self, value, attr, data, **kwargs) -> FileStorage:
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail("invalid")

        return value


class BookSchema(Schema):
    book = FileStorageField(required=True)


class BookQuerySchema(Schema):
    class Meta:
        unknown = INCLUDE

    name = fields.Str(required=True, validate=Length(max=50))
    preview = fields.Boolean(required=False)
