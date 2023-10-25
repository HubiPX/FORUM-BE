from flask import Blueprint, session, request
from sqlalchemy import desc
from database.models import db
from database.models import Users
from database.hash import Hash
from blueprints.auth import Auth

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


@users.route('stats', methods=['get'])
@Auth.logged_user
def _stats_():
    all_users = Users.query.order_by(desc(Users.ranking)).all()

    return [{
        "username": x.username,
        "is_admin": x.admin,
        "last_login": x.last_login,
        "ranking": x.ranking,
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
