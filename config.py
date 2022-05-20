import os

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

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")
    UPLOAD_FOLDER = os.path.join(basedir, "static/uploads/")
    UPLOADED_IMAGES_DEST = os.path.join(UPLOAD_FOLDER, "images")
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
