from datetime import timedelta
import logging

from flask import g
from sqlalchemy import asc

from . import models as m

definitions = []


class ChallengeDef:
    def match_challenge(self, challenge):
        """
        is this definition targeted for the specified challenge object.
        """
        return False

    def is_triggered(self, record):
        """
        will the specified record trigger a progress updating on this challenge.
        """
        raise NotImplementedError

    def initial(self):
        """"
        create initial challenge progress
        """
        raise NotImplementedError

    def on_update(self, progress, record):
        """
        update progress on new record.
        """
        raise NotImplementedError

    def repr(self, progress):
        """
        human readble representation of a challenge progress
        """
        raise NotImplementedError

    @staticmethod
    def find_def(challenge):
        """
        find definition for challenge object.
        """
        for definition in definitions:
            if definition.match_challenge(challenge):
                return definition


class KbswChallenge(ChallengeDef):
    """
    壶铃摆荡挑战
    """

    def __init__(self, total):
        self.total = total

    def match_challenge(self, challenge):
        return challenge.name.startswith('kbsw') \
               and challenge.total == self.total

    def is_triggered(self, record):
        return record.workout.name.startswith('kbsw')

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        progress.achieved = progress.achieved + record.times
        if progress.achieved >= self.total:
            progress.finished = True
        return True

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '壶铃摆荡挑战'


definitions.extend([KbswChallenge(1000), KbswChallenge(3000),
                    KbswChallenge(5000), KbswChallenge(10000)])


class PullUpChallenge(ChallengeDef):
    """
    引体向上挑战
    """

    def __init__(self, total):
        self.total = total

    def match_challenge(self, challenge):
        return challenge.name.startswith('pullup') \
               and challenge.total == self.total

    def is_triggered(self, record):
        return record.workout.name.startswith('pullup')

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        progress.achieved = progress.achieved + record.times
        if progress.achieved >= self.total:
            progress.finished = True
        return True

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '引体向上%s次挑战' % self.total


definitions.extend([PullUpChallenge(100), PullUpChallenge(300),
                    PullUpChallenge(500), PullUpChallenge(1000),
                    PullUpChallenge(3000), PullUpChallenge(5000),
                    PullUpChallenge(10000)])


class PbPressChallenge(ChallengeDef):
    """
    双杠臂屈伸挑战
    """

    def __init__(self, total):
        self.total = total

    def match_challenge(self, challenge):
        return challenge.name.startswith('pbpress') \
               and challenge.total == self.total

    def is_triggered(self, record):
        return record.workout.name.startswith('pbpress')

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        progress.achieved = progress.achieved + record.times
        if progress.achieved >= self.total:
            progress.finished = True
        return True

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '双杠臂屈伸%s次挑战' % self.total


definitions.extend([
    PbPressChallenge(500), PbPressChallenge(1000),
    PbPressChallenge(3000), PbPressChallenge(5000),
    PbPressChallenge(10000)])


class MuscleUpChallenge(ChallengeDef):
    """
    双力臂挑战
    """

    def __init__(self, total):
        self.total = total

    def match_challenge(self, challenge):
        return challenge.name.startswith('muscleup') \
               and challenge.total == self.total

    def is_triggered(self, record):
        return record.workout.name.startswith('muscleup')

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        progress.achieved = progress.achieved + record.times
        if progress.achieved >= self.total:
            progress.finished = True
        return True

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '双力臂%s次挑战' % self.total


definitions.extend([
    MuscleUpChallenge(500), MuscleUpChallenge(1000)
])


class SquatChanllenge(ChallengeDef):
    """
    深蹲挑战
    """

    def __init__(self, total):
        self.total = total * 1000

    def match_challenge(self, challenge):
        return challenge.name.startswith('squat') \
               and challenge.total == self.total

    def is_triggered(self, record):
        workout_name = record.workout.name
        parts = workout_name.split('-', 1)
        return len(parts) >= 2 \
            and parts[0] in ('squat', 'kbsq') \
            and parts[1].isdecimal()

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        parts = record.workout.name.split('-', 1)
        kilo = int(parts[1]) * record.times
        progress.achieved = progress.achieved + kilo
        if progress.achieved >= self.total:
            progress.finished = True
        return True

    def repr(self, progress):
        achieved = progress.achieved / 1000.
        total = progress.challenge.total / 1000.
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '累计负重深蹲%s吨挑战' % (self.total / 1000)


definitions.extend([SquatChanllenge(50), SquatChanllenge(100),
                    SquatChanllenge(200), SquatChanllenge(400),
                    SquatChanllenge(800)])


class ContinuousWorkoutChallenge(ChallengeDef):
    """
    连续打卡挑战
    """

    def __init__(self, total):
        self.total = total

    def match_challenge(self, challenge):
        return challenge.name.startswith('workout') \
               and challenge.total == self.total

    def is_triggered(self, record):
        return True

    def initial(self):
        return {}

    def on_update(self, progress, record):
        if progress.achieved >= self.total:
            return False
        latest_record = m.WorkOutRecord.query \
            .filter_by(id=progress.latest_record_id).first()
        if latest_record is None:
            progress.achieved = 1
            return True
        if latest_record.ts.date() == record.ts.date():
            # hotfix(initial challenge join)
            if progress.achieved == 0:
                progress.achieved += 1
                return True
            return False
        delta = record.ts - latest_record.ts
        if delta < timedelta(days=2):
            progress.achieved += 1
            if progress.achieved >= self.total:
                progress.finished = True
            return True
        logging.info('休息时间超过48小时 %s', delta)
        progress.achieved = 1
        return True

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '连续打卡%s天挑战' % self.total


definitions.extend([ContinuousWorkoutChallenge(30),
                    ContinuousWorkoutChallenge(60),
                    ContinuousWorkoutChallenge(100)])


def show_challenge_progresses(challenges=None):
    if challenges is None:
        user: m.User = g.user
        challenges = user.challenges

    if len(challenges) == 0:
        return f'{user.name} 没有参加任何挑战'

    progresses = []
    for ch in challenges:
        definition = ChallengeDef.find_def(ch.challenge)
        if definition is None:
            continue
        progresses.append(definition.repr(ch))
    return '\n'.join(progresses)


def list_challenges():
    all = m.Challenge.query.filter_by(closed=False).all()
    all_names = '\n'.join(f'{c.name} :: {c.description}' for c in all)
    return f'正在进行中的挑战项目有:\n{all_names}'


def join_challenge(challenge_name):
    challenge = m.Challenge.query \
        .filter_by(closed=False, name=challenge_name).first()
    if challenge is None:
        return f'不存在该挑战项目: {challenge_name}'
    joined = m.ChallengeProgress.query.with_parent(g.user) \
        .filter_by(challenge_id=challenge.id, finished=False).first()
    if joined is not None:
        return f'{g.user.name} 已经参加了挑战-{challenge.description}'

    definition = ChallengeDef.find_def(challenge)
    if definition is None:
        return f'抱歉，挑战活动-{challenge.description} 的规则还没有开发完成.'
    m.add_challenge_progress(g.user, challenge, **definition.initial())
    return f'{g.user} 开始挑战 {challenge.description}'


def update_challenge_progress_for_user(user, records: list):
    updated_progresses = []
    for progress in user.challenges:
        challenge = progress.challenge
        definition = ChallengeDef.find_def(challenge)
        if definition is None:
            logging.warn('no definition found for %s', challenge)
            continue
        updated = False
        for record in records:
            updated = update_progress(user, progress, record, definition) \
                      or updated
        if updated:
            updated_progresses.append(progress)
        m.db.session.add(progress)
    return updated_progresses


def recalculate_challenge_progress_for_user(user):
    for progress in user.challenges:
        challenge = progress.challenge
        definition = ChallengeDef.find_def(challenge)
        if definition is None:
            logging.warn('no definition found for %s', challenge)
            continue
        to_update = definition.initial()
        to_update['achieved'] = 0
        to_update['finished'] = False
        start_record_id = progress.start_record_id
        to_update['latest_record_id'] = start_record_id
        for k, v in to_update.items():
            setattr(progress, k, v)
        m.db.session.add(progress)
        m.db.session.flush()

        records = m.WorkOutRecord.query \
            .with_parent(user) \
            .filter(m.WorkOutRecord.id > start_record_id) \
            .order_by(asc(m.WorkOutRecord.id))

        for record in records:
            update_progress(user, progress, record, definition)
        m.db.session.add(progress)


def update_progress(user, progress, record, definition):
    if progress.finished:
        return False
    if not definition.is_triggered(record):
        return False
    before_change = definition.repr(progress)
    updated = definition.on_update(progress, record)
    progress.latest_record_id = record.id
    after_change = definition.repr(progress)
    logging.info('update progress of %s from %s to %s with %s',
                 user.name, before_change, after_change, record)
    return updated
