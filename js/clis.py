from .app import create_app


def create_db():
  from .models import db
  app = create_app()
  db.create_all(app=app)
