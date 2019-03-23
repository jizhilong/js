#!/usr/bin/env python
# coding: utf8
# author: Ji.Zhilong <zhilongji@gmail.com>
# date: 17/03/2019

from flask import request
from .commands import find_processor
from .app import create_app

app = create_app()

def send_message(channel: str, message: str, *users: [str]):
  '''
  send message to a beary channel, and @ some users.
  '''
  # TODO
  pass


@app.route("/", methods=['POST'])
def index():
  '''
  receive POST from beary chat, dispatch to proper sub commands.
  '''
  data = request.get_json()
  r = BearyChatRequest(data)
  processor = find_processor(r.cmd)
  response = processor(r.cmd)
  return response


class BearyChatRequest:
  def __init__(self, json):
    self.token = json['token']
    self.trigger_word = json['trigger_word']
    self.text = json['text']
    self.cmd = self.text.lstrip(self.trigger_word).strip()
    self.channel = json['channel_name']
    self.user = json['user_name']
    self.ts = json['ts']


if __name__ == '__main__':
  pass
