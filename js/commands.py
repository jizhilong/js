from datetime import datetime, timedelta
import itertools
import logging

from flask import g
from sqlalchemy import desc

from .parsers import parse_command_with_records as pcr
from .parsers import parse_command_with_text_arguments as pct
from . import models as m
from . import challenges as ch

cmd_processors = []


class CmdRegisterItem:
    def __init__(self, func, help_msg="", predicate=None):
        self.func = func
        self.help_msg = help_msg
        if predicate is None:
            self.predicate = lambda cmd: cmd == func.__name__
            self.name = func.__name__
        elif isinstance(predicate, str):
            self.predicate = lambda cmd: cmd == predicate
            self.name = predicate
        else:
            self.predicate = predicate
            self.name = func.__name__

    def is_triggered(self, cmd):
        return self.predicate(cmd)

    def process(self, cmd):
        return self.func(cmd)


def register_cmd(predicate=None, help_msg=''):
    def wrapper(f):
        cmd_processors.append(CmdRegisterItem(f, help_msg, predicate))
        return f
    return wrapper


def parser(parse_func):
    """
    register arg parser to processor functions.
    """
    import functools

    def wrapper(func):
        @functools.wraps(func)
        def process_wrapped(cmdline):
            return func(*parse_func(cmdline))
        return process_wrapped

    return wrapper


@register_cmd('help', help_msg='显示支持的命令列表')
@parser(pct)
def help_cmd(cmd, args: list = None):
    if len(args) == 0:
        commands = ', '.join(p.name for p in cmd_processors)
        return f'支持的命令包括: {commands}'
    else:
        cmd_name = args[0]
        _, processor = find_processor(cmd_name)
        if processor is None or processor is _workout_processor:
            return f'{cmd_name}: 尚不支持此命令'
        return f'{cmd_name}: {processor.help_msg}'


@register_cmd('list', help_msg='显示支持的运动类型')
@parser(pct)
def list_workouts(cmd, _=None):
    names = '\n'.join(f'{w.name}: {w.description}' for w in m.Workout.query.all())
    return names


@register_cmd(help_msg='显示指定运动的教程')
@parser(pct)
def tutorial(cmd, workout):
    return f"this is tutorial for {workout}"


@register_cmd(help_msg='显示最近运动记录')
@parser(pct)
def show(cmd, names: list = None):
    if len(names) == 0:
        return _show_records_for_user(g.user)
    user_name = names[0]
    user = m.User.query.filter_by(name=user_name).first()
    if user is None or (user.invisible and g.user.id != user.id):
        return f'不存在此用户: {user_name}'
    return _show_records_for_user(user)


def _show_records_for_user(user: m.User):
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    records = m.WorkOutRecord.query.with_parent(user)\
        .filter(m.WorkOutRecord.ts > three_days_ago)\
        .order_by(desc(m.WorkOutRecord.ts))

    def group_key(r: m.WorkOutRecord):
        return r.workout.description, r.ts.date().isoformat()

    def merge_records(sub_records):
        lst = []
        for i, sub_iter in itertools.groupby(r.times for r in sub_records):
            count = len([_ for _ in sub_iter])
            if count == 1:
                lst.append(f'{i}')
            else:
                lst.append(f'{i}x{count}')
        return ','.join(lst)

    groups = itertools.groupby(records, group_key)

    records_repr = '\n'.join(f'{date} :: {description}: {merge_records(sub_records)}'
                             for ((description, date), sub_records) in groups)
    if records_repr == '':
        return f'{user.name} 还没有健身记录， 加油哦!'
    return f'{user.name} 最近的打卡记录:\n{records_repr}'


@register_cmd(help_msg='显示运动排行榜')
@parser(pct)
def rank(cmd):
    return f"workout ranking:"


@register_cmd(help_msg='开启隐身模式')
@parser(pct)
def hideme(cmd, _=None):
    print(g.user.invisible)
    g.user.invisible = True
    m.db.session.add(g.user)
    m.db.session.commit()
    return f"{g.user.name} 隐身模式开启"


@register_cmd(help_msg='参与专项挑战')
@parser(pct)
def challenge(cmd, op_or_name=None):
    op = None if len(op_or_name) == 0 else op_or_name[0]
    if op is None:
        has_challenge = len(g.user.challenges) != 0
        if has_challenge:
            return ch.show_challenge_progresses()
        else:
            return ch.list_challenges()
    if op == 'list':
        return ch.list_challenges()
    if op == 'show':
        return ch.show_challenge_progresses()
    if op == 'recalculate':
        ch.recalculate_challenge_progress_for_user(g.user)
        return ch.show_challenge_progresses()
    challenge_name = op
    return ch.join_challenge(challenge_name)


def is_legal_workout_name(name):
    is_cmd_name = any(p.name == name for p in cmd_processors)
    return not is_cmd_name and (name not in {'show', 'list'})


@register_cmd('add-workout', help_msg='添加新的运动类型')
@parser(pct)
def add_workout_type(cmd, args: list = None):
    if len(args) != 2:
        return f'语法不正确，需要以"<name> <description>"形式提供'
    if g.user.id > 3:
        return '权限不足'
    name, description = args
    if not is_legal_workout_name(name):
        return f'{name} 不是合法的运动名'
    workout = m.Workout(name=name, description=description)
    m.db.session.add(workout)
    m.db.session.commit()
    return f'成功添加: {name} - {description}'


def is_workout_name(cmd):
    not_operation_name = not any(item.is_triggered(cmd) for item in cmd_processors)
    return not_operation_name


@parser(pcr)
def workout(name, records):
    logging.info("add records %s of workout %s for user %s", records, name, g.user.name)
    try:
        saved_records, workout = m.add_record(g.user, name, records)
        ch.update_challenge_progress_for_user(g.user, saved_records)
        m.db.session.commit()
    except m.JsError as error:
        return error.msg
    return f'{g.user.name} 打卡:\n{workout.description}: {records}'


_workout_processor = CmdRegisterItem(workout)


def find_processor(cmd_line: str):
    cmd = cmd_line.split()[0]
    for processor in cmd_processors:
        if processor.is_triggered(cmd):
            return cmd, processor
    if is_workout_name(cmd):
        return cmd, _workout_processor
    return cmd, None


def process(cmd_line: str):
    cmd, processor = find_processor(cmd_line)
    if processor is None:
        logging.error("command %s not supported", cmd)
        return
    logging.info("processing with %s", processor.name)
    return processor.process(cmd_line)


if __name__ == '__main__':
    import os
    import sys
    from .app import create_app
    app = create_app()
    with app.app_context():
        g.user, _ = m.get_or_create_user(os.environ.get('USER'))
        logging.basicConfig(level=logging.DEBUG)
        print(process(' '.join(sys.argv[1:])))
