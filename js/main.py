#!/usr/bin/env python
# coding: utf8
# author: Ji.Zhilong <zhilongji@gmail.com>
# date: 17/03/2019

from flask import request, g, jsonify
from .commands import find_processor
from .app import create_app
from . import models as m
import requests

import logging

app = create_app()


@app.route("/js", methods=['POST'])
def bearychat():
    """
    receive POST from beary chat, dispatch to proper sub commands.
    """
    data = request.get_json()
    r = BearyChatRequest(data)
    cmd, processor = find_processor(r.cmd)
    response = {}
    if processor is None:
        response['text'] = f'不存在此命令: {cmd}'
        return jsonify(response)
    g.user = m.get_user(r.user_id)
    if g.user is None:
        response['text'] = f"{r.user_id} 不存在"
        return jsonify(response)
    g.user_name = r.user_name
    response['text'] = processor.process(r.cmd)
    return jsonify(response)


@app.route("/bot/<token>", methods=['POST'])
def telegram(token):
    """
    receive POST from telegram, dispatch to proper sub commands.

    :param token: telegram bot token
    :return: fixed string for ack the message
    """

    try:
        response = _do_process_telegram()
        requests\
            .post(f'https://api.telegram.org/bot{token}/sendMessage',
                  json=response, timeout=2)\
            .raise_for_status()
    except Exception:
        logging.exception("get error")
    return 'ok'


def _do_process_telegram():
    data = request.get_json()
    reason, r = TelegramRequest.validate(data)
    if r is None:
        logging.warning("not valid telegram bot command request: " + reason)
        return
    cmd, processor = find_processor(r.cmd)
    response = {'chat_id': r.chat, 'reply_to_message_id': r.message_id, 'parse_mode': 'Markdown'}
    if processor is None:
        response['text'] = f'不存在此命令: {cmd}'
        return response
    g.user, _ = m.get_or_create_user(r.user_id)
    g.user_name = r.user_name
    response['text'] = processor.process(r.cmd)
    return response


class BearyChatRequest:
    def __init__(self, json):
        self.token = json['token']
        self.trigger_word = json['trigger_word']
        self.text = json['text']
        self.cmd = self.text.lstrip(self.trigger_word).strip()
        self.user_id = json['user_name']
        self.user_name = json['user_name']
        self.channel = json.get('channel_name')
        self.ts = json['ts']


class TelegramRequest:
    def __init__(self, json):
        self.data = json

    @classmethod
    def validate(cls, json):
        if 'message' not in json:
            return 'not a json update', None
        if 'text' not in json['message']:
            return 'no text found in message', None
        entities = json['message'].get('entities', [])
        if not any(e['type'] == 'bot_command' for e in entities):
            return 'not a bot command', None
        cmd_parts = json['message']['text'].split(maxsplit=1)
        if len(cmd_parts) != 2:
            return 'no command supplied', None
        return 'ok', cls(json)

    @property
    def message_id(self):
        return self.data['message']['message_id']

    @property
    def cmd(self):
        return self.data['message']['text'].split(maxsplit=1)[1].strip()

    @property
    def user_id(self):
        return str(self.data['message']['from']['id'])

    @property
    def user_name(self):
        return str(self.data['message']['from']['first_name'])

    @property
    def chat(self):
        return self.data['message']['chat']['id']


if __name__ == '__main__':
    pass
