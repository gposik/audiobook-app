from flask import request
from marshmallow import ValidationError
from ma import ma
from exceptions import APIError
from schemas.base import (
    RequestBodyParamsSchema,
    RequestPathParamsSchema,
    RequestQueryParamsSchema,
)


def schema_check(schema=None, json_data=None, title=None):
    # load and validate
    try:
        return schema.load(data=json_data)

    except ValidationError as err:
        raise APIError(
            status_code=400,
            title=title,
            messages=err.messages,
            data=err.data,
            valid_data=err.valid_data,
        )


def request_schemas_load(schemas):
    if not isinstance(schemas, list):
        schemas = [schemas]

    result_path, result_query, result_body = {}, {}, {}
    for schema in schemas:
        if isinstance(schema, RequestPathParamsSchema):
            # path params
            result_path.update(
                schema_check(
                    schema=schema,
                    json_data=request.view_args,
                    title="One or more request url path parameters did not validate",
                )
            )

        if isinstance(schema, RequestQueryParamsSchema):
            # query params
            result_query.update(
                schema_check(
                    schema=schema,
                    json_data=request.args,
                    title="One or more request url query parameters did not validate",
                )
            )

        if isinstance(schema, (RequestBodyParamsSchema, ma.SQLAlchemyAutoSchema)):
            # body params
            result_body.update(
                schema_check(
                    schema=schema,
                    json_data=request.get_json(),
                    title="One or more request body parameters did not validate",
                )
            )

    return {
        "path": result_path,
        "query": result_query,
        "body": result_body,
    }
