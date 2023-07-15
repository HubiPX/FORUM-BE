import string
from random import choices
from flask import Blueprint, session, request
from database.models import db
from database.models import Users, Posts, Postsa, Postsm, Postsv, Postsnews, Postsbugs, Postssug
from database.hash import Hash
from blueprints.auth import Auth
import re

users = Blueprint('users', __name__)


@users.route('create', methods=['post'])
def _create_():
    post = request.get_json()

    password = post.get("password")
    username = post.get("username")

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
        "is_admin": x.admin
    } for x in all_users]


@users.route('change-password', methods=['post'])
@Auth.logged_user
def _change_password_():
    post = request.get_json()

    current_pwd = post.get("password")
    new_pwd = post.get("new_password")

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
@Auth.logged_mod
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

    if not user:
        return '', 404

    characters = string.ascii_lowercase + string.digits
    new_password = ''.join(choices(characters, k=6))
    hash_pwd = Hash.hash_password(new_password)

    user.password = hash_pwd
    db.session.commit()
    return {"new_password": new_password}


@users.route("/<user_id>/delete", methods=['get'])
@Auth.logged_admin
def _delete_(user_id):
    if user_id == "1":
        return '', 400
    elif not Users.query.filter_by(id=user_id).first():
        return '', 404

    Posts.query.filter_by(owner_id=user_id).delete()
    Postsa.query.filter_by(owner_id=user_id).delete()
    Postsm.query.filter_by(owner_id=user_id).delete()
    Postsv.query.filter_by(owner_id=user_id).delete()
    Postsnews.query.filter_by(owner_id=user_id).delete()
    Postsbugs.query.filter_by(owner_id=user_id).delete()
    Postssug.query.filter_by(owner_id=user_id).delete()

    Users.query.filter_by(id=user_id).delete()
    db.session.commit()
    return '', 200
