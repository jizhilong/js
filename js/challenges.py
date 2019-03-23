from flask import g

from . import models as m


class ChallengeDef:
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


def show_challenge_progresses():
    user: m.User = g.user
    challenges = user.challenges
    if len(challenges) == 0:
        return f'{user.name} 没有参加任何挑战'

    return '\n'.join(repr(c) for c in challenges)


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

    m.add_challenge_progress(g.user.name, challenge_name)
    return f'{g.user.name} 开始挑战 {challenge.description}'
