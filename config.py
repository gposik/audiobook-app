import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 14400))
    ALLOWED_MIMETYPES_EXTENSIONS = set(
        ["image/apng", "image/bmp", "image/jpeg", "image/png", "image/svg+xml"]
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    APISPEC_SPEC = APISpec(
        title="Audiobook Builder",
        version="v1",
        plugins=[MarshmallowPlugin()],
        openapi_version="2.0.0",
    )
    APISPEC_SWAGGER_URL = "/swagger/"  # URI to access API Doc JSON
    APISPEC_SWAGGER_UI_URL = "/swagger-ui/"  # URI to access UI of API Doc

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")
    UPLOAD_FOLDER = os.path.join(basedir, "static/uploads/")
    UPLOADED_FILES_DEST = os.path.join(UPLOAD_FOLDER, "files")
    UPLOADED_IMAGES_DEST = os.path.join(UPLOAD_FOLDER, "images")
    UPLOADED_AUDIOS_DEST = os.path.join(UPLOAD_FOLDER, "audios")
    UPLOADED_BOOKS_DEST = os.path.join(UPLOAD_FOLDER, "books")
    UPLOADED_BOOKS_ALLOW = ("mobi", "pdf", "epub")


class TestingConfig(Config):
    TESTING = True


class StagingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("STAGE_DATABASE_URL")


class ProductionConfig(Config):
    DEBUG = False


env_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
}
