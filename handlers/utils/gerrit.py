from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
from pygerrit2.rest import GerritRestAPI
import datetime

class GerritChangeFetcher():
    gerrit_url = "https://review.lineageos.org/" # Needs a trailing slash
    rest = GerritRestAPI(url=gerrit_url)

    @classmethod
    def get_change(self, changenum):
        # Use DETAILED_ACCOUNTS so we don't have to make a second API call for owner email and name
        change = self.rest.get("/changes/{}?o=DETAILED_ACCOUNTS".format(changenum))
        return {
            "fallback": "{}#/c/{}: {}".format(self.gerrit_url,change['_number'],change['subject']),
            "color": "good",
            "title": "{}: {} ({})".format(change['_number'], change['subject'], 'Open' if change['status'] == 'NEW' else change['status'].capitalize()),
            "title_link": "{}#/c/{}".format(self.gerrit_url,change['_number']),
            "mrkdwn_in": ["text"],
            'text': ("*Project*: <{base}#/q/project:{project}|{project}> ({branch})\n"
                     "*Topic*: {topic}\n"
                     "*Owner*: <{base}#/q/owner:{username}|{name} ({email})>")
                .format(
                    project = change['project'],
                    branch = change['branch'],
                    topic = '<{}#/q/{topic}|{topic}>'.format(self.gerrit_url, topic = change['topic']) if 'topic' in change else 'None',
                    username = change['owner']['username'],
                    name = change['owner']['name'],
                    email = change['owner']['email'],
                    base = self.gerrit_url,
                )
                }

    @classmethod
    def get_topic(self, topic_name):
        topic = self.rest.get("/changes/?q=topic:{}".format(topic_name))
        t_changes = ocn = mcn = acn = omcn = 0
        # Initialise these separately (unlike before), so we don't end up with
        # projects == branches
        projects,branches = [],[]
        for change in topic:
            if change['project'] not in projects:
                projects.append(change['project'])
            if change['branch'] not in branches:
                branches.append(change['branch'])
            if change['status'] == 'NEW':
                ocn = ocn + 1
                if change['mergeable']:
                    omcn = omcn + 1
            if change['status'] == 'MERGED':
                mcn = mcn + 1
            if change['status'] == 'ABANDONED':
                acn = acn + 1
            t_changes = t_changes + 1
        return {
            "fallback": "Topic: {}".format(topic_name),
            "color": "good",
            "title": "Topic: {}".format(topic_name),
            "title_link": "{}#/q/topic:{}".format(self.gerrit_url,topic_name),
            "mrkdwn_in": ["text"],
            "text": ("{total} commits across {projects} projects on {branches} branch(es)\n"
                     "*Open*: <{base}#/q/status:open%20AND%20topic:{name}|{ocn}>, "
                             "of which <{base}#/q/status:open%20AND%20is:mergeable%20AND%20topic:{name}|{omcn}> are mergeable\n"
                     "*Merged*: <{base}#/q/status:merged%20AND%20topic:{name}|{mcn}>\n"
                     "*Abandoned*: <{base}#/q/status:abandoned%20AND%20topic:{name}|{acn}>")
                .format(
                    projects = len(projects),
                    branches = len(branches),
                    total = t_changes,
                    base = self.gerrit_url,
                    name = topic_name,
                    ocn = ocn,
                    omcn = omcn,
                    mcn = mcn,
                    acn = acn,
                )
          }

