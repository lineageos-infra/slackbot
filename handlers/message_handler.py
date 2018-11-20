import re
import traceback

import requests

from itertools import islice
from .utils.gerrit import GerritChangeFetcher

gerrit_url = 'https://review.lineageos.org/'

def send_response(client, event, response=None, attachments=None):
    if response and attachments:
        client.api_call('chat.postMessage', channel=event['channel'], text=response, attachments=attachments)
    elif response:
        client.api_call('chat.postMessage', channel=event['channel'], text=response)
    elif attachments:
        client.api_call('chat.postMessage', channel=event['channel'], attachments=attachments)
def process_message(event, client):
    try:
        m = event['text']
        if m.startswith('!'):
            #Command mode!
            if m[1:].startswith("vend"):
                req = requests.get('https://itvends.com/vend.php')
                if req.status_code == 200:
                    send_response(client, event, response='It vends {}!'.format(req.text[:-1]))
        if re.search(gerrit_url.replace('.', r'\.'), m):
            number = 0
            attachments = []
            for word in m.split():
                if 'review.lineageos.org' in word:
                    if number >= 4:
                        break
                    number += 1
                    topic = re.search(r'(?:topic:)(.+?(?:(?=[%\s+]|$|>)))',word)
                    change = re.search(gerrit_url.replace('.', r'\.') + '(?:(?:#\/)?c\/(?:LineageOS\/[a-zA-Z_0-9\-]*\/\+\/)?)?([0-9]+)',word)
                    if change:
                        attachments.append(GerritChangeFetcher.get_change(change.group(1)))
                    elif topic:
                        attachments.append(GerritChangeFetcher.get_topic(topic.group(1)))
            send_response(client, event, attachments=attachments)
        if re.search(r'karma', m, re.IGNORECASE):
            return 'BOT HAS PIMPED VARIOUS KARMA', None
        if re.search(r'CVE-\d{4}-\d{4,7}', m):
            '''Grab CVEs from cve.cirl.lu'''
            attachments = []
            match_iter = re.finditer(r'CVE-\d{4}-\d{4,7}', m)
            for match in islice(match_iter, 4):
                cve = match.group(0)
                url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cve)
                req = {}
                try:
                    req = requests.get("https://cve.circl.lu/api/cve/{}".format(cve))
                except requests.exceptions.Timeout:
                    summary = "Request timed out"
                    attachments.append({"fallback": "{}: {} ({})".format(cve, summary, url), "color": "danger", "title": "{}: {}".format(cve, summary), "title_link": url})
                    continue
                if req.status_code == 200:
                    try:
                        summary = req.json()['summary']
                        attachments.append({"fallback": "{}: {} ({})".format(cve, summary, url), "color": "danger", "title": "{}: {}".format(cve, summary), "title_link": url})
                    except Exception as e:
                        print(e)
                        pass
            send_response(client, event, attachments=attachments)
    except Exception as e:
        #This is a horrible workaround. Exception happens, future dies if we're not calling wait(). Just print/log the message and let it finish.
        traceback.print_exc()
