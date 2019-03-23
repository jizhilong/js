class ParseError(Exception):
    def __init__(self, text):
        super().__init__(self, text)
        self.text = text


def parse_records(text):
    """parse workout records

        '' -> []
        50 -> [50]
        50x5 -> [50, 50, 50, 50, 50]
        50*5 -> [50, 50, 50, 50, 50]
        50,40,40,40,40 -> [50, 40, 40, 40, 40]
        50,40x4 -> [50, 40, 40, 40, 40]
        50,40*4 -> [50, 40, 40, 40, 40]
     """

    def multi_parser(op, content):
        parts = content.split(op)
        if not (len(parts) == 2 and all(part.isdecimal() for part in parts)):
            raise ParseError(content)
        times = int(parts[0])
        groups = int(parts[1])
        return [times] * groups

    def sub_parser(content):
        """
        '' -> []
        50 -> [50]
        50x5 -> [50, 50, 50, 50, 50]
        50*5 -> [50, 50, 50, 50, 50]
        """
        content = content.strip()
        if content == '':
            return []
        if content.isdecimal():
            return [int(content)]

        for op in '*x':
            if op in content:
                return multi_parser(op, content)
        raise ParseError(content)

    allowed_characters = '*x,0123456789'
    if not all(c in allowed_characters for c in text):
        raise ParseError(text)
    result = []
    for sub_text in text.split(','):
        result.extend(sub_parser(sub_text))
    return result


def parse_command_with_text_arguments(text: str):
    """parse command name and text arguments from command line.

  'show' -> ('show', [])
  'show ycqian zlji' -> ('show', ['ycqian', 'zlji'])
  'challenge pullup -> ('challenge', ['pullup'])
    """
    parts = text.split()
    cmd = parts[0]
    args = parts[1:]
    return cmd, args


def parse_command_with_records(text: str):
    """parse command name and records from command line.

  'kbsw-12 50' -> ('kbsw-12', [50])
  'kbsw-12 50x3' -> ('kbsw-12', [50, 50, 50])
  'kbsw-12 50x3,60' -> ('kbsw-12', [50, 50, 50, 60])
    """

    cmd, record_parts = text.split()
    return cmd, parse_records(record_parts)


def test_parse_records():
    assert parse_records('') == []
    assert parse_records('50') == [50]
    assert parse_records('50*5') == [50, 50, 50, 50, 50]
    assert parse_records('50x5') == [50, 50, 50, 50, 50]
    assert parse_records('50,40,40,40,40') == [50, 40, 40, 40, 40]
    assert parse_records('50,40*4') == [50, 40, 40, 40, 40]


def test_parse_command_with_text_arguments():
    assert parse_command_with_text_arguments('show') == ('show', [])
    assert parse_command_with_text_arguments('show ycqian zlji') == ('show', ['ycqian', 'zlji'])
    assert parse_command_with_text_arguments('challenge pullup') == ('challenge', ['pullup'])


def test_parse_command_with_records():
    assert parse_command_with_records('kbsw-12 50') == ('kbsw-12', [50])
    assert parse_command_with_records('kbsw-12 50x3') == ('kbsw-12', [50, 50, 50])
    assert parse_command_with_records('kbsw-12 50x3,60') == ('kbsw-12', [50, 50, 50, 60])
