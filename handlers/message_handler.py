import re

from .utils.gerrit import GerritChangeFetcher

gerrit_url = 'https://review.lineageos.org/'

def process_message(m):
    if re.search(gerrit_url.replace('.', r'\.'), m):
        number = 0
        response = []
        for word in m.split():
            if 'review.lineageos.org' in word:
                if number >= 4:
                    break
                number += 1
                topic = re.search(r'(?:topic:)(.+?(?:(?=[%\s+]|$|>)))',word)
                change = re.search(r'(?:' + gerrit_url.replace('.', r'\.') + ')(?:(?:#\/c\/)|)([0-9]{4,7})',word)
                if change:
                    response.append(GerritChangeFetcher.get_change(change.group(1)))
                elif topic:
                    response.append(GerritChangeFetcher.get_topic(topic.group(1)))
        return None, response


    if re.search(r'.*FOOBAR.*', m):
        return 'FOOBAR!', None
