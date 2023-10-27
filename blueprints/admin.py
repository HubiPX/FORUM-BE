import string
from random import choices
from flask import Blueprint, session, request
from database.models import db
from database.models import Users, Posts, Postsa, Postsm, Postsv, Postsnews, Postsbugs, Postssug
from database.hash import Hash
from blueprints.auth import Auth
import re
import datetime


admin = Blueprint('admin', __name__)


@admin.route('', methods=['get'])
@Auth.logged_admin
def _users_():
    all_users = Users.query.all()

    return [{
        "id": x.id,
        "username": x.username,
        "admin": x.admin,
        "ban": x.ban_date,
        "last_login": x.last_login,
        "score": x.score,
        "vip_date": x.vip_date,
        "ranking": x.ranking,
        "color_nick": x.color_nick,
        "rank": x.rank
    } for x in all_users]


@admin.route("/<user_id>/set-score", methods=['post'])
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


@admin.route("<user_id>/reset-password", methods=['get'])
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


@admin.route("<user_id>/lvl-admin", methods=['post'])
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

    if is_admin == '1':
        if user.vip_date is None:
            today = datetime.datetime.now()
            vip_date = today + datetime.timedelta(days=30)
            user.vip_date = vip_date
        else:
            vip_date = user.vip_date + datetime.timedelta(days=30)
            user.vip_date = vip_date
    else:
        user.vip_date = None

    user.admin = is_admin

    db.session.commit()
    return '', 200


@admin.route("/<user_id>/delete", methods=['post'])
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
