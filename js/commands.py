from datetime import datetime, timedelta
import itertools
import logging
import string

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


def longest_common_suffix(s1: str, s2: str):
    l1, l2 = len(s1), len(s2)
    i = min(len(s1), len(s2))
    while i > 0 and s1[l1-i:] != s2[l2-i:]:
        i -= 1
    return s1[l1-i:]


def merge_name(prefix, workouts):
    suffixes = '|'.join(w.name.lstrip(prefix) for w in workouts)
    return f'{prefix}[{suffixes}]'


def merge_description(workouts):
    descriptions = [w.description for w in workouts]
    common = descriptions[0]
    for description in descriptions[1:]:
        common = longest_common_suffix(common, description)
    common = common.lstrip(string.digits)
    prefixes = '|'.join(d.rstrip(common) for d in descriptions)
    return f'[{prefixes}]{common}'


@register_cmd('list', help_msg='列出所有支持的运动项目')
@parser(pct)
def list_workouts(cmd, _=None):
    workouts = [w for w in m.Workout.query.all()]
    workouts.sort(key=lambda w: w.name)
    names = []
    for name, group in itertools.groupby(workouts,
                                         lambda w: w.name.split('-', 1)[0]):
        group_workouts = [w for w in group]
        if len(group_workouts) == 1:
            names.append(f'{group_workouts[0].name}: {group_workouts[0].description}')
        else:
            merged_name = merge_name(name, group_workouts)
            merged_description = merge_description(group_workouts)
            names.append(f'{merged_name}: {merged_description}')
    names = '\n'.join(names)
    return f'```\n{names}\n```'


@register_cmd(help_msg='显示指定运动的教程')
@parser(pct)
def tutorial(cmd, workout):
    return f"this is tutorial for {workout}"


_default_show_days = 3


def _parse_days(days_str: str):
    try:
        if days_str.isdecimal():
            return int(days_str)
    except ValueError:
        return _default_show_days
    return _default_show_days


@register_cmd(help_msg='显示最近运动记录')
@parser(pct)
def show(cmd, names: list = None):
    if len(names) == 0:
        return _show_records_for_user(g.user, _default_show_days)

    user_name, days = names[0], _default_show_days
    if len(names) == 1 and user_name.isdecimal():
        return _show_records_for_user(g.user, _parse_days(names[0]))

    if len(names) >= 2:
        days = _parse_days(names[1])
    user = m.User.query.filter_by(name=user_name).first()
    if user is None or (user.invisible and g.user.id != user.id):
        return f'不存在此用户: {user_name}'
    return _show_records_for_user(user, days)


def _show_records_for_user(user: m.User, days: int):
    days_ago = datetime.utcnow() - timedelta(days=days)
    records = m.WorkOutRecord.query.with_parent(user)\
        .filter(m.WorkOutRecord.ts > days_ago) \
        .order_by(desc(m.WorkOutRecord.ts)) \
        .limit(1000)

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
        return f'{user} 最近{days}天没有健身记录， 加油哦!'
    return f'{user} 最近{days}天的打卡记录:\n{records_repr}'


@register_cmd(help_msg='显示运动排行榜')
@parser(pct)
def rank(cmd):
    return f"workout ranking:"


@register_cmd(help_msg='开启隐身模式')
@parser(pct)
def hideme(cmd, args=None):
    invisible = True
    if len(args) == 1 and args[0] == 'off':
        invisible = False
    g.user.invisible = invisible
    m.db.session.add(g.user)
    m.db.session.commit()
    if invisible:
        return f"隐身模式开启"
    else:
        return f"隐身模式关闭"


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
        m.db.session.commit()
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
    logging.info("add records %s of workout %s for user %s", records, name, g.user_name)
    try:
        saved_records, workout = m.add_record(g.user, name, records)
        updated_progresses =\
            ch.update_challenge_progress_for_user(g.user, saved_records)
        m.db.session.commit()
    except m.JsError as error:
        return error.msg
    record_message = f'打卡:\n{workout.description}: {records}'
    if len(updated_progresses) == 0:
        return record_message
    else:
        return f'{record_message}\n' \
               f'{ch.show_challenge_progresses(updated_progresses)}'


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
        user_name = os.environ.get('USER')
        g.user = m.get_user(user_name)
        if g.user is None:
            print(f"{user_name} 不存在")
        else:
            logging.basicConfig(level=logging.DEBUG)
            print(process(' '.join(sys.argv[1:])))
            m.db.session.commit()
