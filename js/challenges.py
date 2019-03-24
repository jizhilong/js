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

    def match_challenge(self, challenge):
        return challenge.name.startswith('kbsw')

    def is_triggered(self, record):
        return record.workout.name.startswith('kbsw')

    def initial(self):
        return {}

    def on_update(self, progress, record):
        progress.achieved = progress.achieved + record.times

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user.name
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '壶铃摆荡挑战'


definitions.append(KbswChallenge())


class PullUpChallenge(ChallengeDef):
    """
    引体向上挑战
    """

    def match_challenge(self, challenge):
        return challenge.name.startswith('pullup')

    def is_triggered(self, record):
        return record.workout.name == 'pullup'

    def initial(self):
        return {}

    def on_update(self, progress, record):
        progress.achieved = progress.achieved + record.times

    def repr(self, progress):
        achieved = progress.achieved
        total = progress.challenge.total
        desc = progress.challenge.description
        user = progress.user.name
        if achieved < total:
            return f'💪️{user} {desc} :: {achieved}/{total}'
        else:
            return f'👍恭喜{user}完成{desc} :: {achieved}/{total}'

    def __str__(self):
        return '引体向上挑战'


definitions.append(PullUpChallenge())


def show_challenge_progresses():
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
    challenge = m.Challenge.query\
        .filter_by(closed=False, name=challenge_name).first()
    if challenge is None:
        return f'不存在该挑战项目: {challenge_name}'
    joined = m.ChallengeProgress.query.with_parent(g.user)\
        .filter_by(challenge_id=challenge.id).first()
    if joined is not None:
        return f'{g.user.name} 已经参加了挑战-{challenge.description}'

    definition = ChallengeDef.find_def(challenge)
    if definition is None:
        return f'抱歉，挑战活动-{challenge.description} 的规则还没有开发完成.'
    m.add_challenge_progress(g.user, challenge, **definition.initial())
    return f'{g.user.name} 开始挑战 {challenge.description}'


def update_challenge_progress_for_user(user, records: list):
    for progress in user.challenges:
        challenge = progress.challenge
        definition = ChallengeDef.find_def(challenge)
        if definition is None:
            logging.warn('no definition found for %s', challenge)
            continue
        for record in records:
            update_progress(user, progress, record, definition)
        m.db.session.add(progress)


def recalculate_challenge_progress_for_user(user):
    for progress in user.challenges:
        challenge = progress.challenge
        definition = ChallengeDef.find_def(challenge)
        if definition is None:
            logging.warn('no definition found for %s', challenge)
            continue
        to_update = definition.initial()
        to_update['achieved'] = 0
        start_record_id = progress.start_record_id
        to_update['latest_record_id'] = start_record_id
        for k, v in to_update.items():
            setattr(progress, k, v)
        m.db.session.add(progress)
        m.db.session.flush()

        records = m.WorkOutRecord.query\
            .with_parent(user)\
            .filter(m.WorkOutRecord.id > start_record_id)\
            .order_by(asc(m.WorkOutRecord.id))

        for record in records:
            update_progress(user, progress, record, definition)
        m.db.session.add(progress)


def update_progress(user, progress, record, definition):
    if not definition.is_triggered(record):
        return
    before_change = definition.repr(progress)
    definition.on_update(progress, record)
    progress.latest_record_id = record.id
    after_change = definition.repr(progress)
    logging.info('update progress of %s from %s to %s with %s',
                 user.name, before_change, after_change, record)
