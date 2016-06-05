from couchbase.bucket import Bucket
import time
import os
import riotwatcher


def main():
    bkt = Bucket('couchbase://localhost/match_history')
    migrate_players(bkt)
    # migrate_matches(bkt)


def migrate_matches(bkt):
    rows = bkt.query('test', 'test')
    for row in rows:
        doc = bkt.get(row.key).value
        player_id = doc['summonerId']
        for game in doc['games']:
            new_key = 'Match::{}::{}'.format(player_id, game['gameId'])
            new_game = game
            new_game['summonerId'] = player_id
            bkt.upsert(new_key, new_game)


def migrate_players(bkt):
    doc = bkt.get('players').value
    riot = riotwatcher.RiotWatcher(
        default_region=riotwatcher.EUROPE_WEST,
        key=os.environ.get('RIOT_API_KEY'))

    for player_id in doc.itervalues():
        summoner = riot.get_summoner(_id=player_id)
        new_key = 'Player::{}'.format(player_id)
        bkt.upsert(new_key, summoner)
        time.sleep(5)


def add_champions(bkt):
    riot = riotwatcher.RiotWatcher(
        default_region=riotwatcher.EUROPE_WEST,
        key=os.environ.get('RIOT_API_KEY'))
    champs = riot.static_get_champion_list()
    champ_dict = {}
    for champ in champs['data'].itervalues():
        champ_dict[int(champ['id'])] = {'key': champ['key'],
                                        'name': champ['name']}
    bkt.upsert('Champions', champ_dict)

if __name__ == '__main__':
    main()