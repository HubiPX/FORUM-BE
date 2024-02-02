from flask import Blueprint, session, request
from sqlalchemy import desc
from database.models import db
from database.models import Users
from database.hash import Hash
from blueprints.auth import Auth

users = Blueprint('users', __name__)


@users.route('/create', methods=['post'])
def _create_():
    post = request.get_json()

    repassword = post.get("repassword")
    password = post.get("password")
    username = post.get("username")

    if password != repassword:
        return 'Podane hasła są różne!', 406

    if len(password) < 3:
        return 'Hasło jest za krótkie!', 400
    elif len(username) < 3:
        return 'Login jest za krótki!', 400
    elif len(password) > 20:
        return 'Hasło jest za długie!', 400
    elif len(username) > 15:
        return 'Login jest za długi!', 400

    hash_pwd = Hash.hash_password(password)

    if Users.query.filter_by(username=username).first():
        return 'Jest już użytkownik o takim nicku.', 406

    new_user = Users(username=username, password=hash_pwd)

    db.session.add(new_user)
    db.session.commit()
    return 'Utworzono konto pomyślnie!', 201


@users.route('/stats', methods=['get'])
@Auth.logged_user
def _stats_():
    all_users = Users.query.order_by(desc(Users.ranking)).all()

    return [{
        "id": x.id,
        "username": x.username,
        "admin": x.admin,
        "last_login": x.last_login,
        "ranking": x.ranking,
        "score": x.score,
        "vip_date": x.vip_date,
        "place": all_users.index(x) + 1,
        "cnick_date": x.cnick_date,
        "rank_date": x.rank_date,
        "color_nick": x.color_nick,
        "rank": x.rank
    } for x in all_users]


@users.route('/change-password', methods=['post'])
@Auth.logged_user
def _change_password_():
    post = request.get_json()

    current_pwd = post.get("password")
    new_pwd = post.get("new_password")
    new_pwd2 = post.get("new_password2")

    if new_pwd != new_pwd2:
        return 'Nowe hasła są różne.', 406

    if not current_pwd or not new_pwd or not new_pwd2:
        return 'Wypełnij wszystkie pola.', 400
    elif len(new_pwd) < 3:
        return 'Nowe hasło jest za krótkie.', 400
    elif len(new_pwd) > 20:
        return 'Nowe hasło jest za długie.', 400
    elif current_pwd == new_pwd:
        return 'Nowe hasło musi być inne niż obecne.', 400

    user = Users.query.filter_by(id=session["user_id"]).first()

    if not Hash.verify_password(user.password, current_pwd):
        return 'Stare hasło jest błędne.', 400

    pwd_hash = Hash.hash_password(new_pwd)
    user.password = pwd_hash
    db.session.commit()
    return '', 200
