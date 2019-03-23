import flask

from . import models


def create_app():
    app = flask.Flask("js")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///js.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    models.init_app(app)
    return app
