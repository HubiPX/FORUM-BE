import os


class Config:
    SECRET_KEY = "sekret"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath("database/database.db")}'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
