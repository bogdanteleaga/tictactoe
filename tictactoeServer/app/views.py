import random
from app import app, models, db, auth
from flask import Flask, request, jsonify, g, url_for, abort
from tictactoeGame import TicTacToe

count = 0
games = {}


@auth.verify_password
def verify_password(username_or_token, password):
    """Verifies user password or token"""
    user = models.User.verify_auth_token(username_or_token)
    if not user:
        user = models.User.query.filter_by(nickname=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    """Returns token for authentication"""
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/users', methods=['POST'])
def new_user():
    """Creates a new user"""
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing args
    if models.User.query.filter_by(nickname=username).first():
        abort(400)  # existing user
    user = models.User(nickname=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.nickname}), 201,
            {'Location': url_for('get_user', id=user.id,
                                 _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    """Returns information about user<id>"""
    user = models.User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.nickname})


@app.route('/api/getmatch')
@auth.login_required
def get_match_id():
    """Returns a match id

    If an even number of players have connected creates a new match
    Else it adds the user as the 2nd player in the previously created match
    """
    global count
    match_id = len(models.Match.query.all())
    if count == 0:
        match_id = match_id + 1  # new match
        m = models.Match(id=match_id, p1=g.user)
        db.session.add(m)
        db.session.commit()
        count = 1
    else:
        m = models.Match.query.filter_by(id=match_id).first()
        m.p2 = g.user
        db.session.add(m)
        db.session.commit()
        count = 0
    return jsonify({'match_id': match_id})


@app.route('/api/match/<int:match_id>', methods=['GET', 'POST'])
@auth.login_required
def get_match(match_id):
    """Returns or commits match information"""
    global games
    m = models.Match.query.filter_by(id=match_id).first()
    player = get_player_info(m, g.user)
    if not m or not player:
        abort(400)
    if match_id not in games:
        games[match_id] = TicTacToe()
    game = games[match_id]

    if request.method == 'GET':
        response = {'Board': game.display(),
                    'XO': 'X' if player == 1 else 'O',
                    'Move': can_move(player, game),
                    'Win': game.win()}
        return jsonify(response)

    if request.method == 'POST':
        move = request.json.get('move')
        if not move:
            abort(400)
        if game.set_cell(move, 'X' if player == 1 else 'O'):
            determine_winner(game, m)
            response = {'Board': game.display(),
                        'XO': 'X' if player == 1 else 'O',
                        'Move': can_move(player, game),
                        'Win': game.win()}
            return jsonify(response)
        return "Invalid move", 400


"""Helper functions for get_match"""


def determine_winner(game, match):
    """Determines winner and updates database"""
    if game.win():
        w = game.win()
        if w == 'X':
            winner = 1
        elif w == 'O':
            winner = 2
        else:
            winner = -1
        match.winner = winner
        db.session.add(match)
        db.session.commit()


def get_player_info(match, user):
    """Is the player 1st or 2nd in match?"""
    player = None
    if match.p1 == user:
        player = 1
    if match.p2 == user:
        player = 2
    return player


def can_move(player, game):
    """Is it this player's turn?"""
    if player == 1:
        if game.last_move == 'X':
            move = 0
        else:
            move = 1
    elif player == 2:
        if game.last_move == 'O':
            move = 0
        else:
            move = 1
    return move
