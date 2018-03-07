import json
import os
import sys

from flask import Flask, request

from slackclient import SlackClient

app = Flask(__name__)
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

if not client_id or not client_secret:
    print("Please source env")
    sys.exit(1)


print("Please see https://lineageandroid.slack.com/oauth?client_id={}&scope=bot&single_channel=0&redirect_uri=https://lux.zifnab.net/lineageos/slackbot/auth".format(client_id))

@app.route("/auth")
def auth():
    code = request.args.get("code")
    client = SlackClient("")
    auth_response = client.api_call("oauth.access", client_id=client_id, client_secret=client_secret, code=code, redirect_uri="https://lux.zifnab.net/lineageos/slackbot/auth")
    with open("auth.json", "w") as f:
        f.write(json.dumps(auth_response))
    return "Authed", 200

if __name__ == "__main__":
    app.run(port=9040)
