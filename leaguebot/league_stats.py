import flask
from flask import Flask, render_template
import core.buckets as buckets
import utils
app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def show_index():
    player_q = buckets.match_history.query('player', 'all_players')
    player_count = sum(1 for _ in player_q)

    match_q = buckets.match_history.query('match', 'all_matches', reduce=False)
    match_count = sum(1 for _ in match_q)

    return render_template('pages/index.html', player_count=player_count,
                           match_count=match_count)


@app.route('/players')
def show_players():
    players = buckets.match_history.query('player', 'all_players',
                                          include_docs=True)
    players = [player.doc.value for player in players]
    return render_template('pages/players.html', players=players)


@app.route('/player/<string:player_name>')
def show_player(player_name):
    raw_champions = buckets.match_history.get('Champions').value
    champions = {}

    # Have to convert to int as this is not easy within
    # the jinja template and the key is unicode for some reason
    for champ_id, value in raw_champions.iteritems():
        champions[int(champ_id)] = value

    player_name = player_name.lower().replace(" ", "")
    player_id = buckets.match_history.query('player', 'all_players',
                                            mapkey_single=player_name, limit=1)
    try:
        player_id = next(player_id.__iter__()).value
    except StopIteration:
        flask.abort(404)

    player_dict = buckets.match_history.get('Player::{}'
                                            .format(player_id)).value
    matches = buckets.match_history.query(
        'match', 'by_player', include_docs=True, mapkey_single=str(player_id),
        reduce=False)

    matches = [match.doc.value for match in matches]
    return render_template('pages/player.html',
                           player_name=player_dict['name'],
                           matches=matches, champions=champions,
                           epoch_to_datetime=utils.epoch_to_datetime)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
