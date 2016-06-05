import logging
import os
import riotwatcher
import sys
import time

from couchbase import exceptions as cb_exceptions
from couchbase.bucket import Bucket

SLEEP_TIME = 15

stream_handler = logging.StreamHandler()
log_format = logging.Formatter(
    fmt='%(levelname)s|%(name)s: %(message)s')
logger_datapop = logging.getLogger('datapop')
stream_handler.setLevel(level=logging.INFO)
stream_handler.setFormatter(fmt=log_format)
logger_datapop.setLevel(logging.DEBUG)
logger_datapop.addHandler(stream_handler)


class MatchHistoryUpdater(object):
    def __init__(self):
        self.riot = riotwatcher.RiotWatcher(
            default_region=riotwatcher.EUROPE_WEST,
            key=os.environ.get('RIOT_API_KEY'))
        self.bucket = Bucket('couchbase://{}/{}'.format(
            os.environ.get('DB_HOST', 'localhost'),
            os.environ.get('DB_BUCKET_MATCH_HISTORY', 'match_history')
        ))

        self.players = self.get_players()
        logger_datapop.info('Setup complete')
        while True:
            for player in self.players:
                self.update_recent_games(player['id'])
                time.sleep(SLEEP_TIME)
            self.players = self.get_players()

    def get_players(self):
        players = [row.doc.value for row in self.bucket.query(
            'player', 'all_players', stale=False, include_docs=True)]
        return players

    def update_recent_games(self, player_id):
        api_matches = self.riot.get_recent_games(player_id)['games']
        for match in api_matches:
            match['summonerId'] = player_id
            key = 'Match::{}::{}'.format(player_id, match['gameId'])
            try:
                self.bucket.insert(key, match)
            except cb_exceptions.KeyExistsError:
                break

            try:
                full_match = self.riot.get_match(match_id=match['gameId'],
                                                 include_timeline=True)
                time.sleep(SLEEP_TIME)
            except Exception:
                continue
            else:
                full_match_key = 'Match::{}'.format(match['gameId'])
                self.bucket.upsert(full_match_key, full_match)

if __name__ == '__main__':
    MatchHistoryUpdater()
