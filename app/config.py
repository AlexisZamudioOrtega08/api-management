import os
from dotenv import load_dotenv
from datetime import timedelta


class Config:
    def __init__(self) -> None:
        self.load_environment_var()
        self.ENV = os.getenv("ENV")
        self.KEY = os.getenv("SECRET_KEY")
        self.API_PREFIX = os.getenv("API_PREFIX")
        self.JWT_TOKEN_LOCATION = ["cookies"]
        self.CSRF_TOKEN_LOCATION = ["cookies"]
        self.JWT_COOKIE_SECURE = True
        self.JWT_COOKIE_CSRF_PROTECT = False
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

        if self.ENV == "development":
            self.development()
        elif self.ENV == "testing":
            self.testing()
        elif self.ENV == "production":
            self.production()

    def load_environment_var(self):
        """
        This function load environments variables y return a tuple with state and Error specification in case.
        """
        path = os.path.dirname(os.path.abspath(__file__)) + "/.env"
        if os.path.exists(path):
            load_dotenv(path)
            while os.getenv("FLAG") is None:
                load_dotenv(path)
        else:
            raise FileNotFoundError("File .env not found")

    def development(self):
        self.DEBUG = True
        self.TESTING = True
        self.DB_CONFIG = {
            "host": os.getenv("MYSQL_DATABASE_HOST_DEV"),
            "user": os.getenv("MYSQL_DATABASE_USER_DEV"),
            "password": os.getenv("MYSQL_DATABASE_PASSWORD_DEV"),
            "db": os.getenv("MYSQL_DATABASE_DB_DEV"),
        }
        self.SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(
            self.DB_CONFIG["user"],
            self.DB_CONFIG["password"],
            self.DB_CONFIG["host"],
            self.DB_CONFIG["db"],
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.JWT_COOKIE_SECURE = False

    def testing(self):
        self.DEBUG = False
        self.TESTING = True
        self.DB_CONFIG = {
            "host": os.getenv("MYSQL_DATABASE_HOST_TEST"),
            "user": os.getenv("MYSQL_DATABASE_USER_TEST"),
            "password": os.getenv("MYSQL_DATABASE_PASSWORD_TEST"),
            "db": os.getenv("MYSQL_DATABASE_DB_TEST"),
        }
        self.SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(
            self.DB_CONFIG["user"],
            self.DB_CONFIG["password"],
            self.DB_CONFIG["host"],
            self.DB_CONFIG["db"],
        )

    def production(self):
        self.DEBUG = False
        self.TESTING = False
        self.DB_CONFIG = {
            "host": os.getenv("MYSQL_DATABASE_HOST_PROD"),
            "user": os.getenv("MYSQL_DATABASE_USER_PROD"),
            "password": os.getenv("MYSQL_DATABASE_PASSWORD_PROD"),
            "db": os.getenv("MYSQL_DATABASE_DB_PROD"),
        }
        self.SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(
            self.DB_CONFIG["user"],
            self.DB_CONFIG["password"],
            self.DB_CONFIG["host"],
            self.DB_CONFIG["db"],
        )


config = {
    "default": Config(),
}
