from flask import Flask
from website.views import registerBlueprints
from website.extensions import db

def create_app(config):
    app = Flask(__name__)
    app.config.from_object('config')
    

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'

    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    registerBlueprints(app)
    
    return app
