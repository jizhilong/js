from .parsers import parse_command_with_records as pcr
from .parsers import parse_command_with_text_arguments as pct

cmd_processors = []


def register_cmd(predicate=None):
    def wrapper(f):
        if predicate is None:
            p = lambda cmd: cmd == f.__name__
        elif isinstance(predicate, str):
            p = lambda cmd: cmd == predicate
        else:
            p = predicate
        cmd_processors.append((p, f))
        return f

    return wrapper


def parser(parse_func):
    """
    register arg parser to processor functions.
    """

    def wrapper(func):
        def process(cmdline):
            return func(*parse_func(cmdline))

        return process

    return wrapper


@register_cmd('help')
@parser(pct)
def help_cmd(cmd, arg=None):
    return f"this is help for {arg}"


@register_cmd('list')
@parser(pct)
def list_workouts(cmd):
    return f"supported workout types:"


@register_cmd
@parser(pct)
def tutorial(cmd, workout):
    return f"this is tutorial for {workout}"


@register_cmd
@parser(pct)
def show(cmd, name=None):
    return f"recent workout records for {name}:"


@register_cmd
@parser(pct)
def rank(cmd):
    return f"workout ranking:"


@register_cmd
@parser(pct)
def hideme(cmd):
    return f"I will hide you."


@register_cmd
@parser(pct)
def challenge(cmd, op_or_name=None):
    return f"challeenge: {op_or_name}."


__registered = [predicate for predicate, _ in cmd_processors]


def is_workout_name(cmd):
    not_operation_name = not any(predicate(cmd) for predicate in __registered)
    return not_operation_name


@register_cmd(predicate=is_workout_name)
@parser(pcr)
def workout(name, records):
    return f"add records {records} for {name}"


def find_processor(cmd_line: str):
    cmd = cmd_line.split()[0]
    for predicate, processor in cmd_processors:
        if predicate(cmd):
            return processor
    return None


def process(cmd_line: str):
    processor = find_processor(cmd_line)
    if processor is None:
        return f"command {cmd_line} not supported"
    print(f"processing with {processor.__name__} ")
    return processor(cmd_line)
