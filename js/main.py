#!/usr/bin/env python
# coding: utf8
# author: Ji.Zhilong <zhilongji@gmail.com>
# date: 17/03/2019

from flask import request, g, jsonify
from .commands import find_processor
from .app import create_app
from . import models as m

app = create_app()


def send_message(channel: str, message: str, *users: [str]):
    """
    send message to a beary channel, and @ some users.
    """
    # TODO
    pass


@app.route("/js", methods=['POST'])
def index():
    """
    receive POST from beary chat, dispatch to proper sub commands.
    """
    data = request.get_json()
    r = BearyChatRequest(data)
    cmd, processor = find_processor(r.cmd)
    response = {}
    if processor is None:
        response['text'] = f'不存在此命令: {cmd}'
        return response
    g.user, _ = m.get_or_create_user(r.user)
    response['text'] = processor.process(r.cmd)
    return jsonify(response)


class BearyChatRequest:
    def __init__(self, json):
        self.token = json['token']
        self.trigger_word = json['trigger_word']
        self.text = json['text']
        self.cmd = self.text.lstrip(self.trigger_word).strip()
        self.user = json['user_name']
        self.channel = json.get('channel_name')
        self.ts = json['ts']


if __name__ == '__main__':
    pass
