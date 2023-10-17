import json
from flask import Blueprint, request, session, Response
from database.models import Users
from database.models import db
from database.hash import Hash
import datetime
import random

login = Blueprint('login', __name__)


@login.route('', methods=['post'])
def _login_():
    post = request.get_json()

    username = post.get("username")
    password = post.get("password")

    if not username or not password:
        return '', 400

    user = Users.query.filter_by(username=username).first()

    if not user or not Hash.verify_password(user.password, password):
        return '', 401

    today = datetime.datetime.now()

    if user.ban_date is not None:
        if user.ban_date < today:
            user.ban_date = None
        else:
            return {"ban_date": user.ban_date}, 403

    if user.last_login is None:
        user.last_login = today
        user.score = 10
        user.ranking = 10
        secret_numbers = random.sample(range(0, 10), 6)
        user.secret_numbers = ''.join(map(str, secret_numbers))
        user.game = ""
        user.game_info = ""
    elif today.date() != user.last_login.date():
        user.score += 10
        user.ranking += 10
        user.last_login = today
        user.game = ""
        user.game_info = ""
        secret_numbers = random.sample(range(0, 10), 6)
        user.secret_numbers = ''.join(map(str, secret_numbers))
    elif today.date() == user.last_login.date():
        user.last_login = today

    session['logged_in'] = True
    session['user_id'] = user.id
    db.session.commit()
    return {"username": user.username, "is_admin": user.admin, "user_id": user.id}, 200
