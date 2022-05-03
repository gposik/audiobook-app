import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = "LOLoTech92"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 14400))
    UPLOAD_FOLDER = os.path.join(basedir, "static/uploads/")
    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif", "svg", "bmp", "pdf", "mobi"])
    ALLOWED_MIMETYPES_EXTENSIONS = set(
        ["image/apng", "image/bmp", "image/jpeg", "image/png", "image/svg+xml"]
    )
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


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


# Validation messages
ALREADY_EXISTS = "{} with that {} already exists"
CREATED_SUCCESSFULLY = "{} created successfully"
NOT_FOUND = "{} not found"
DELETED = "{} deleted"
