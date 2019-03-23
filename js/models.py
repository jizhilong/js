import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

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
    invisible = db.Column(db.Boolean, default=False)
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
    description = db.Column(db.String(1024), nullable=False)
    records = db.relationship('WorkOutRecord', backref='workout', lazy=True)

    def __repr__(self):
        return '<WorkOut %r>' % self.name

    @staticmethod
    def create_builtin_workouts():
        workouts = [
            Workout(name='kbsw-4', description='4公斤壶铃摆荡'),
            Workout(name='kbsw-8', description='8公斤壶铃摆荡'),
            Workout(name='kbsw-12', description='12公斤壶铃摆荡'),
            Workout(name='kbsw-16', description='16公斤壶铃摆荡'),
            Workout(name='kbsw-24', description='24公斤壶铃摆荡'),

            Workout(name='kbdl-4', description='4公斤壶铃硬拉'),
            Workout(name='kbdl-8', description='8公斤壶铃硬拉'),
            Workout(name='kbdl-12', description='12公斤壶铃硬拉'),
            Workout(name='kbdl-16', description='16公斤壶铃硬拉'),
            Workout(name='kbdl-24', description='24公斤壶铃硬拉'),

            Workout(name='kbsq-4', description='4公斤壶铃深蹲'),
            Workout(name='kbsq-8', description='8公斤壶铃深蹲'),
            Workout(name='kbsq-12', description='12公斤壶铃深蹲'),
            Workout(name='kbsq-16', description='16公斤壶铃深蹲'),
            Workout(name='kbsq-24', description='24公斤壶铃深蹲'),

            Workout(name='kbcl-4', description='4公斤壶铃高翻'),
            Workout(name='kbcl-8', description='8公斤壶铃高翻'),
            Workout(name='kbcl-12', description='12公斤壶铃高翻'),
            Workout(name='kbcl-16', description='16公斤壶铃高翻'),
            Workout(name='kbcl-24', description='24公斤壶铃高翻'),

            Workout(name='kbsn-4', description='4公斤壶铃抓举'),
            Workout(name='kbsn-8', description='8公斤壶铃抓举'),
            Workout(name='kbsn-12', description='12公斤壶铃抓举'),
            Workout(name='kbsn-16', description='16公斤壶铃抓举'),
            Workout(name='kbsn-24', description='24公斤壶铃抓举'),

            Workout(name='kbpr-4', description='4公斤壶铃实力举'),
            Workout(name='kbpr-8', description='8公斤壶铃实力举'),
            Workout(name='kbpr-12', description='12公斤壶铃实力举'),
            Workout(name='kbpr-16', description='16公斤壶铃实力举'),
            Workout(name='kbpr-24', description='24公斤壶铃实力举'),

            Workout(name='squat', description='徒手深蹲'),
            Workout(name='squat-20', description='20公斤颈后深蹲'),
            Workout(name='squat-40', description='40公斤颈后深蹲'),
            Workout(name='squat-50', description='50公斤颈后深蹲'),
            Workout(name='squat-60', description='60公斤颈后深蹲'),
            Workout(name='squat-70', description='70公斤颈后深蹲'),
            Workout(name='squat-80', description='80公斤颈后深蹲'),
            Workout(name='squat-90', description='90公斤颈后深蹲'),
            Workout(name='squat-100', description='100公斤颈后深蹲'),
            Workout(name='squat-110', description='110公斤颈后深蹲'),
            Workout(name='squat-120', description='120公斤颈后深蹲'),
            Workout(name='squat-130', description='130公斤颈后深蹲'),
            Workout(name='squat-140', description='140公斤颈后深蹲'),

            Workout(name='dlift-20', description='20公斤硬拉'),
            Workout(name='dlift-40', description='40公斤硬拉'),
            Workout(name='dlift-50', description='50公斤硬拉'),
            Workout(name='dlift-60', description='60公斤硬拉'),
            Workout(name='dlift-70', description='70公斤硬拉'),
            Workout(name='dlift-80', description='80公斤硬拉'),
            Workout(name='dlift-90', description='90公斤硬拉'),
            Workout(name='dlift-100', description='100公斤硬拉'),
            Workout(name='dlift-110', description='110公斤硬拉'),
            Workout(name='dlift-120', description='120公斤硬拉'),
            Workout(name='dlift-130', description='130公斤硬拉'),
            Workout(name='dlift-140', description='140公斤硬拉'),

            Workout(name='pullup', description='自重引体向上'),
            Workout(name='pullup-aid', description='辅助引体向上'),

            Workout(name='pushup', description='俯卧撑'),
            Workout(name='parbar-press', description='双杠臂屈伸'),
            Workout(name='burpee', description='波比跳'),
        ]

        for workout in workouts:
            db.session.add(workout)
        db.session.commit()


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
    total = db.Column(db.Integer, nullable=False)


def _latest_record_id():
    return db.session.query(func.max(WorkOutRecord.id)).scalar() or 0


class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    achieved = db.Column(db.Integer, nullable=False, default=0)
    start_record_id = db.Column(db.Integer, nullable=True, default=_latest_record_id)
    latest_record_id = db.Column(db.Integer, nullable=True, default=_latest_record_id)
    memo = db.Column(db.String(2048), nullable=True)

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


def add_challenge(name, total):
    challenge = Challenge(name=name, total=total)
    db.session.add(challenge)
    db.session.commit()
    return challenge


def add_challenge_progress(user_name, challenge_name):
    user, _ = get_or_create_user(user_name)
    challenge = Challenge.query.filter_by(name=challenge_name).first()
    if challenge is None:
        raise JsError(f"不存在名为 {challenge_name} 的挑战")
    progress = ChallengeProgress.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()
    if progress is not None:
        raise JsError(f"{user_name} 已经参加了挑战 {challenge_name}")
    progress = ChallengeProgress(user=user, challenge=challenge)
    db.session.add(progress)
    db.session.commit()
    return progress


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


@_with_db
def test_add_challenge_progress():
    challenge = add_challenge('kbsw-10000', 10000)
    add_record('user', 'kbsw-16', [50, 50, 50])
    progress = add_challenge_progress('user', 'kbsw-10000')

    assert progress.user.name == "user"
    assert progress.challenge.name == challenge.name
    assert progress.start_record_id == 3
    assert progress.latest_record_id == 3
    assert progress.achieved == 0


if __name__ == '__main__':
    from .app import create_app
    app = create_app()
    with app.app_context():
        db.create_all(app=app)
        Workout.create_builtin_workouts()
