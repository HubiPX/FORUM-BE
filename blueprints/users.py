import string
from random import choices
from flask import Blueprint, session, request
from sqlalchemy import desc
from database.models import db
from database.models import Users, Posts, Postsa, Postsm, Postsv, Postsnews, Postsbugs, Postssug
from database.hash import Hash
from blueprints.auth import Auth
import re
import datetime

users = Blueprint('users', __name__)


@users.route('create', methods=['post'])
def _create_():
    post = request.get_json()

    repassword = post.get("repassword")
    password = post.get("password")
    username = post.get("username")

    if password != repassword:
        return '', 422

    if len(password) < 3 or len(username) < 3:
        return '', 400

    hash_pwd = Hash.hash_password(password)

    if Users.query.filter_by(username=username).first():
        return '', 422

    new_user = Users(username=username, password=hash_pwd, admin=0)

    db.session.add(new_user)
    db.session.commit()
    return '', 201


@users.route('', methods=['get'])
@Auth.logged_admin
def _users_():
    all_users = Users.query.all()

    return [{
        "id": x.id,
        "username": x.username,
        "is_admin": x.admin,
        "ban": x.ban_date,
        "last_login": x.last_login,
        "score": x.score
    } for x in all_users]


@users.route('stats', methods=['get'])
@Auth.logged_user
def _stats_():
    all_users = Users.query.order_by(desc(Users.score)).all()

    return [{
        "username": x.username,
        "is_admin": x.admin,
        "last_login": x.last_login,
        "score": x.score,
        "place": all_users.index(x) + 1
    } for x in all_users]


@users.route('change-password', methods=['post'])
@Auth.logged_user
def _change_password_():
    post = request.get_json()

    current_pwd = post.get("password")
    new_pwd = post.get("new_password")
    new_pwd2 = post.get("new_password2")

    if new_pwd != new_pwd2:
        return '', 422

    if not current_pwd or not new_pwd or len(new_pwd) < 3 or current_pwd == new_pwd:
        return '', 400

    user = Users.query.filter_by(id=session["user_id"]).first()

    if not Hash.verify_password(user.password, current_pwd):
        return '', 401

    pwd_hash = Hash.hash_password(new_pwd)
    user.password = pwd_hash
    db.session.commit()
    return '', 200


@users.route("<user_id>/lvl-admin", methods=['post'])
@Auth.logged_admin
def _lvl_admin_(user_id):
    post = request.get_json()
    is_admin = post.get("admin")

    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()
    user = Users.query.filter_by(id=user_id).first()

    if not user:
        return '', 404
    elif user.id == 1 or not re.match("^[0-4]*$", is_admin) \
            or int(user.admin) >= int(you.admin) or int(you.admin) <= int(is_admin):
        return '', 403

    user.admin = is_admin

    db.session.commit()
    return '', 200


@users.route("<user_id>/reset-password", methods=['get'])
@Auth.logged_admin
def _reset_password_(user_id):
    user = Users.query.filter_by(id=user_id).first()
    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()

    if not user:
        return '', 404
    elif int(user.admin) >= int(you.admin):
        return '', 403

    characters = string.ascii_lowercase + string.digits
    new_password = ''.join(choices(characters, k=6))
    hash_pwd = Hash.hash_password(new_password)

    user.password = hash_pwd
    db.session.commit()
    return {"new_password": new_password}


@users.route("/<user_id>/set-score", methods=['post'])
@Auth.logged_admin
def _set_score_(user_id):
    user = Users.query.filter_by(id=user_id).first()
    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return '', 404
    elif int(user.admin) > int(you.admin):
        return '', 403

    post = request.get_json()
    new_score = post.get("new_score")

    try:
        score = int(new_score)
    except ValueError:
        return '', 400

    if not score >= 0:
        return '', 400

    user.score = score

    db.session.commit()
    return '', 200


@users.route("/<user_id>/store", methods=['post'])
@Auth.logged_user
def _store_(user_id):
    user = Users.query.filter_by(id=user_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return '', 404

    post = request.get_json()
    score = post.get("score")

    try:
        score = int(score)
    except ValueError:
        return '', 400

    if not 0 < score <= 10000:
        return '', 400

    x = user.score
    if x >= score:
        x = x - score
        user.score = x
    else:
        return '', 400

    db.session.commit()
    return '', 200


@users.route('game', methods=['post'])
@Auth.logged_user
def _game_():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
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

    db.session.commit()
    return '', 200


@users.route('game-info', methods=['get'])
@Auth.logged_user
def _game_info_():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    return {"game": user.game, "game_info": user.game_info}


@users.route("/<user_id>/delete", methods=['post'])
@Auth.logged_admin
def _delete_(user_id):
    user = Users.query.filter_by(id=user_id).first()
    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()

    if user_id == "1":
        return '', 401
    elif not Users.query.filter_by(id=user_id).first():
        return '', 404
    elif int(user.admin) >= int(you.admin):
        return '', 403

    post = request.get_json()
    days = post.get("days")

    try:
        time = int(days)
    except ValueError:
        return '', 400

    if time == 0:
        user.ban_date = None
    elif 0 < time < 366:
        today = datetime.datetime.now()
        ban = today + datetime.timedelta(days=time)
        user.ban_date = ban
    elif time == 2580:
        Posts.query.filter_by(owner_id=user_id).delete()
        Postsa.query.filter_by(owner_id=user_id).delete()
        Postsm.query.filter_by(owner_id=user_id).delete()
        Postsv.query.filter_by(owner_id=user_id).delete()
        Postsnews.query.filter_by(owner_id=user_id).delete()
        Postsbugs.query.filter_by(owner_id=user_id).delete()
        Postssug.query.filter_by(owner_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
    else:
        return '', 400

    db.session.commit()
    return '', 200
