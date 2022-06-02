class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "gauravardak"

    DB_NAME = "production-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"

    UPLOADS = "/home/username/app/app/static/images/uploads"

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"

    UPLOADS = "/home/username/projects/flask_test/app/app/static/images/uploads"

    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"

    UPLOADS = "/home/username/projects/flask_test/app/app/static/images/uploads"

    SESSION_COOKIE_SECURE = False