import datetime
import logging

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
        return f'{self.name}{self.badges}'

    @property
    def badges(self):
        finished_challenge_no = ChallengeProgress.query\
            .with_parent(self).filter_by(finished=True).count()
        badge = '🏋'
        numbers = '⓪①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'
        if finished_challenge_no == 0:
            return ''
        if finished_challenge_no < 3:
            return badge*finished_challenge_no
        if finished_challenge_no < len(numbers):
            return badge + numbers[finished_challenge_no]
        return badge + f'^{finished_challenge_no}'


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
        return f'{self.name}-{self.description}'

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
            if Workout.query.filter_by(name=workout.name).first() is None:
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

    def __repr__(self):
        return '%s-%s' % (self.workout.description, self.times)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(1024), default='')
    closed = db.Column(db.Boolean, default=False)
    total = db.Column(db.Integer, nullable=False)

    @staticmethod
    def create_builtin_challenges():
        challenges = [
            Challenge(name='kbsw-10000', description='一万次壶铃摆荡', total=10000),
            Challenge(name='pullup-1000', description='一千次引体向上', total=1000),
            Challenge(name='squat-50', description='累计深蹲50吨', total=50*1000),
            Challenge(name='squat-100', description='累计深蹲100吨', total=100*1000),
            Challenge(name='squat-200', description='累计深蹲200吨', total=200*1000),
            Challenge(name='workout-30d', description='连续打卡30天', total=30),
            Challenge(name='workout-60d', description='连续打卡60天', total=60),
            Challenge(name='workout-100d', description='连续打卡100天', total=100),
            Challenge(name='pbpress-1000', description='一千次双杠臂屈伸', total=1000),
            Challenge(name='muscleup-1000', description='一千次双力臂', total=1000),
        ]
        for c in challenges:
            if Challenge.query.filter_by(name=c.name).first() is None:
                db.session.add(c)
        db.session.commit()

    def __repr__(self):
        return f'{self.name}-{self.description}'


def _latest_record_id():
    return db.session.query(func.max(WorkOutRecord.id)).scalar() or 0


class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    achieved = db.Column(db.Integer, nullable=False, default=0)
    start_record_id = db.Column(db.Integer, nullable=True, default=_latest_record_id)
    latest_record_id = db.Column(db.Integer, nullable=True, default=_latest_record_id)
    memo = db.Column(db.String(2048), nullable=True)
    finished = db.Column(db.Boolean, default=False)

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


def add_record(user_or_name, workout_name, groups):
    if isinstance(user_or_name, str):
        user, _ = get_or_create_user(user_or_name)
    else:
        user = user_or_name
    workout = Workout.query.filter_by(name=workout_name).first()
    if workout is None:
        raise JsError(f'项目: {workout_name} 不存在')
    dt = datetime.datetime.utcnow()
    records = []
    for times in groups:
        record = WorkOutRecord(user_id=user.id, workout_id=workout.id, times=times, ts=dt)
        records.append(record)
        db.session.add(record)
    db.session.flush()
    return records, workout


def add_command(user_name, command_text):
    user, _ = get_or_create_user(user_name)
    user.commands.append(Command(text=command_text))
    db.session.commit()


def add_challenge(name, total):
    challenge = Challenge(name=name, total=total)
    db.session.add(challenge)
    db.session.commit()
    return challenge


def add_challenge_progress(user_or_name, challenge_or_name, **kwargs):
    assert user_or_name is not None
    assert challenge_or_name is not None
    if isinstance(user_or_name, str):
        user, _ = get_or_create_user(user_or_name)
    else:
        user = user_or_name
    if isinstance(challenge_or_name, str):
        challenge = Challenge.query.filter_by(name=challenge_or_name).first()
    else:
        challenge = challenge_or_name
    if challenge is None:
        raise JsError(f"不存在名为 {challenge_or_name} 的挑战")
    progress = ChallengeProgress.query.filter_by(user_id=user.id,
                                                 challenge_id=challenge.id,
                                                 finished=False).first()
    if progress is not None:
        raise JsError(f"{user_or_name} 已经参加了挑战 {challenge_or_name}")
    progress = ChallengeProgress(user=user, challenge=challenge, **kwargs)
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
    Workout.create_builtin_workouts()
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
    Workout.create_builtin_workouts()
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
        logging.info('创建数据库')
        db.create_all(app=app)
        logging.info('添加内置运动类型')
        Workout.create_builtin_workouts()
        logging.info('添加内置挑战类型')
        Challenge.create_builtin_challenges()
