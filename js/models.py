import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)


class JsError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    records = db.relationship('WorkOutRecord', backref='user', lazy=True)
    commands = db.relationship('Command', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.name


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    ts = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    records = db.relationship('WorkOutRecord', backref='workout', lazy=True)

    def __repr__(self):
        return '<WorkOut %r>' % self.name


class WorkOutRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    times = db.Column(db.Integer, nullable=False)

    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'),
                           nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    achived = db.Column(db.Integer, nullable=False)

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'),
                             nullable=False)
    challenge = db.relationship('Challenge', backref=db.backref('progresses', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User', backref=db.backref('challenges', lazy=True))


def get_or_create_user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        user = User(name=name)
        db.session.add(user)
        db.session.flush()
        return user, True
    return user, False


def add_record(user_name, workout_name, groups):
    user, _ = get_or_create_user(user_name)
    workout = Workout.query.filter_by(name=workout_name).first()
    if workout is None:
        if user.id > 3:
            raise JsError(f'项目: {workout_name} 不存在')
        workout = Workout(name=workout_name)
        db.session.add(workout)
        db.session.flush()
    dt = datetime.datetime.utcnow()
    for times in groups:
        record = WorkOutRecord(user_id=user.id, workout_id=workout.id, times=times, ts=dt)
        db.session.add(record)
    db.session.commit()


def add_command(user_name, command_text):
    user, _ = get_or_create_user(user_name)
    user.commands.append(Command(text=command_text))
    db.session.commit()


def __init_db():
    import flask
    app = flask.Flask("js")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_app(app)
    db.create_all(app=app)
    return app


def _with_db(f):
    def wrapped(*args, **kwargs):
        app = __init_db()
        with app.app_context():
            f(*args, **kwargs)
        db.drop_all(app=app)

    return wrapped


@_with_db
def test_add_user():
    assert User.query.count() == 0
    user1 = User(name='user1')
    user2 = User(name='user2')
    db.session.add(user1)
    db.session.add(user2)
    db.session.flush()

    assert user1.id == 1
    assert user2.id == 2
    users = User.query.all()
    assert len(users) == 2

    for user in users:
        assert user.name in ['user1', 'user2']


@_with_db
def test_add_record():
    add_record('user', 'kbsw-16', [50, 50, 50])

    user = User.query.filter_by(name='user').first()
    assert user is not None
    assert len(user.records) == 3
    workout = Workout.query.filter_by(name='kbsw-16').first()
    assert workout is not None
    assert len(workout.records) == 3


@_with_db
def test_add_command():
    add_command('user', 'kbsw-16 50*5')

    user = User.query.filter_by(name='user').first()
    assert user is not None
    assert len(user.commands) == 1
    assert user.commands[0].text == 'kbsw-16 50*5'


def test():
    test_add_user()
    test_add_record()
    test_add_command()
    print("test finished")