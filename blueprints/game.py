from flask import Blueprint, session, request
from database.models import db
from database.models import Users
from blueprints.auth import Auth
import re

game = Blueprint('game', __name__)


@game.route('game', methods=['post'])
@Auth.logged_user
def _game_():
    user = Users.query.filter_by(id=session["user_id"]).first()
    secret = user.secret_numbers

    post = request.get_json()
    try_numbers = post.get("try_numbers")

    if len(try_numbers) != 6 or not re.match("^[0-9]*$", try_numbers) or try_numbers == "":
        return '', 400

    if user.game is None:
        user.game = try_numbers
        user.game_info = ""
    elif user.game[-6:] == secret:
        return '', 400
    elif user.game[-6:] == try_numbers:
        return '', 406
    elif len(user.game) == 24:
        return '', 400
    else:
        user.game += try_numbers

    game_info = ""

    for i in range(6):
        if secret[i] == try_numbers[i]:
            game_info = game_info + "2"
        elif try_numbers[i] in secret:
            game_info = game_info + "1"
        else:
            game_info = game_info + "0"

    user.game_info += game_info

    if secret == try_numbers:
        user.score += 100
        user.ranking += 100

    db.session.commit()
    return '', 200


@game.route('game-info', methods=['get'])
@Auth.logged_user
def _game_info_():
    user = Users.query.filter_by(id=session["user_id"]).first()
    return {"game": user.game, "game_info": user.game_info}
