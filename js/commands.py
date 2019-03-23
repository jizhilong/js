import logging

from .parsers import parse_command_with_records as pcr
from .parsers import parse_command_with_text_arguments as pct
from . import models as m

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
def show(cmd, name=None):
    return f"recent workout records for {name}:"


@register_cmd(help_msg='显示运动排行榜')
@parser(pct)
def rank(cmd):
    return f"workout ranking:"


@register_cmd(help_msg='开启隐身模式')
@parser(pct)
def hideme(cmd):
    return f"I will hide you."


@parser(pct)
def challenge(cmd, op_or_name=None):
    return f"challenge: {op_or_name}."


def is_workout_name(cmd):
    not_operation_name = not any(item.is_triggered(cmd) for item in cmd_processors)
    return not_operation_name


@parser(pcr)
def workout(name, records):
    return f"add records {records} for {name}"


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
    import sys
    from .app import create_app
    app = create_app()
    with app.app_context():
        logging.basicConfig(level=logging.DEBUG)
        print(process(' '.join(sys.argv[1:])))
