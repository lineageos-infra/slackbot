import logging
import time

import praw

from .db import DataStore
from .plugin import Plugin

class Reddit(Plugin):
    plugin = 'reddit'
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger('root')
        self.done = DataStore.get(self.plugin, 'done')
        self.logger.debug("processed messages: %d", len(self.done))
        if not self.done:
            self.done = []
            DataStore.save(self.plugin, 'done', self.done)

    def loop(self):
        while True:
            try:
                r = praw.Reddit(user_agent='LineageOS Slack Bot v1.0')
                r.read_only = True
                for post in r.subreddit('lineageos').new(limit=10):
                    if post.id in self.done:
                        continue
                    attachment = {
                        'fallback': post.url,
                        'pretext': 'reddit',
                        'title': post.title,
                        'title_link': post.url,
                        'text': post.selftext[:140] if hasattr(post, 'selftext') else ''
                    }
                    self.client.api_call('chat.postMessage', channel='C62RNKJTZ', attachments=[attachment], unfurl_links=True)
                    self.done.append(post.id)
                    DataStore.save(self.plugin, 'done', self.done)
            except Exception as e:
                print(e)
                pass
            time.sleep(60)

if __name__ == '__main__':
    reddit = Reddit()
    reddit.loop()
