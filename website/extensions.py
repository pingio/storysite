import os
from flask import Flask
from flask.config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _get_config():
    # Workaround to get an available config object before the app is initiallized
    # Only needed/used in top-level and class statements
    # https://stackoverflow.com/a/18138250/7597273
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config = Config(root_path)
    config.from_object('config')
    return config

config = _get_config()