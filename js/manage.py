from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from .app import create_app
from . import models  as m

app = create_app()
migrate = Migrate(app, m.db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def rename(old_name, new_name):
    user = m.get_user(old_name)
    if user is None:
        print(f"user {old_name} not found.")
        return
    user.name = new_name
    m.db.session.commit()
    print(f'renamed {old_name} to {new_name}')


if __name__ == '__main__':
    manager.run()
