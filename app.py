# -*- coding: utf-8 -*-
"""
In this file, we'll create a routing layer to handle incoming and outgoing
requests between our bot and Slack.
"""
import os
import jinja2
import json
import time

from concurrent.futures import ThreadPoolExecutor

from flask import make_response, render_template
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

from handlers import process_message

from plugins import Reddit

from log import setup_custom_logger
logger = setup_custom_logger('root')

# Load client_id/client_secret
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
verification = os.environ.get("VERIFICATION_TOKEN")
token=""

client = None #SlackClient("")
events_adapter = SlackEventAdapter(verification, "/events") 
template_loader = jinja2.ChoiceLoader([
                    events_adapter.server.jinja_loader,
                    jinja2.FileSystemLoader(['templates']),
                  ])
events_adapter.server.jinja_loader = template_loader

executor = ThreadPoolExecutor(max_workers=4)

@events_adapter.on("message")
def handle_message(event_data):
    event = event_data['event']
    if 'bot_id' in event or 'text' not in event:
        return
    executor.submit(process_message, event, client)

@events_adapter.server.before_first_request
def before_first_request():
    if not client_id:
        print("Can't find Client ID, did you set this env variable?")
    if not client_secret:
        print("Can't find Client Secret, did you set this env variable?")
    if not verification:
        print("Can't find Verification Token, did you set this env variable?")

if __name__ == '__main__':
    try:
        with open("auth.json", "r") as f:
            auth = json.loads(f.read())
            client = SlackClient(auth["bot"]["bot_access_token"])
    except Exception as e:
        print(e)
        print("No token registered, please run oauth.py")
    debug = False
    if 'DEBUG' in os.environ:
        debug = True
    executor.submit(events_adapter.start, debug=debug, port=9040)

    reddit = Reddit(client)

    executor.submit(reddit.loop)
    while True:
        time.sleep(60)
