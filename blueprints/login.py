import json
from flask import Blueprint, request, session, Response
from database.models import Users
from database.hash import Hash

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

    session['logged_in'] = True
    session['user_id'] = user.id
    return {"username": user.username, "is_admin": user.admin, "user_id": user.id}, 200
