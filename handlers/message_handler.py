import re

import requests

from itertools import islice
from .utils.gerrit import GerritChangeFetcher

gerrit_url = 'https://review.lineageos.org/'

def process_message(m):
    if m.startswith('!'):
        #Command mode!
        if m[1:].startswith("vend"):
            req = requests.get('https://itvends.com/vend.php')
            if req.status_code == 200:
                return 'It vends {}!'.format(req.text[:-1]), None
    if re.search(gerrit_url.replace('.', r'\.'), m):
        number = 0
        response = []
        for word in m.split():
            if 'review.lineageos.org' in word:
                if number >= 4:
                    break
                number += 1
                topic = re.search(r'(?:topic:)(.+?(?:(?=[%\s+]|$|>)))',word)
                change = re.search(r'(?:' + gerrit_url.replace('.', r'\.') + ')(?:(?:#\/c\/)|)(?:LineageOS\/[a-zA-Z_0-9\-]*\/\+\/)([0-9]{4,7})',word)
                if change:
                    response.append(GerritChangeFetcher.get_change(change.group(1)))
                elif topic:
                    response.append(GerritChangeFetcher.get_topic(topic.group(1)))
        return None, response
    if re.search(r'karma', m, re.IGNORECASE):
        return 'BOT HAS PIMPED VARIOUS KARMA', None
    if re.search(r'CVE-\d{4}-\d{4,7}', m):
        '''Grab CVEs from cve.cirl.lu'''
        response = []
        match_iter = re.finditer(r'CVE-\d{4}-\d{4,7}', m)
        for match in islice(match_iter, 4):
            cve = match.group(0)
            url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cve)
            req = {}
            try:
                req = requests.get("https://cve.circl.lu/api/cve/{}".format(cve), timeout=1)
            except requests.exceptions.Timeout:
                summary = "Request timed out"
                response.append({"fallback": "{}: {} ({})".format(cve, summary, url), "color": "danger", "title": "{}: {}".format(cve, summary), "title_link": url})
                continue
            if req.status_code == 200:
                try:
                    summary = req.json()['summary']
                    response.append({"fallback": "{}: {} ({})".format(cve, summary, url), "color": "danger", "title": "{}: {}".format(cve, summary), "title_link": url})
                except Exception as e:
                    print(e)
                    pass
        return None, response
    return None, None
