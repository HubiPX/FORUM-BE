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
        "cnick_date": x.cnick_date,
        "rank_date": x.rank_date,
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
        return 'Brak takiego uzytkownika.', 404
    elif int(user.admin) > int(you.admin):
        return 'Poziom admina tego użytkownika jest większy niż twój!', 403

    post = request.get_json()
    new_score = post.get("new_score")

    try:
        score = int(new_score)
    except ValueError:
        return 'Wprowadzona wartość nie jest liczbą.', 400

    if not score >= 0:
        return 'Wprowadz liczbę większą od 0.', 400

    user.score = score

    db.session.commit()
    return f'Ustawiono ilość expa użytkownikowi {user.username} na: {user.score}!', 200


@admin.route("<user_id>/reset-password", methods=['get'])
@Auth.logged_admin
def _reset_password_(user_id):
    user = Users.query.filter_by(id=user_id).first()
    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()

    if not user:
        return 'Brak takiego użytkownika.', 404
    elif int(user.admin) >= int(you.admin):
        return 'Twój poziom admina jest zbyt niski.', 403

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
    days = 0

    try:
        int(is_admin)
    except ValueError:
        return 'Wprowadzona wartość nie jest liczbą.', 400

    if len(is_admin) > 1 and is_admin[0] == '1':
        if 1 <= int(is_admin[1:]) < 366:
            days = int(is_admin[1:])
            print(days)
            is_admin = '1'
        elif is_admin[0] == '1':
            return 'Błędna ilość dni dla VIPa wprowadź 1-365.', 400
    elif len(is_admin) == 1 and is_admin[0] == '1':
        return 'Nie wprowadzono ilości dni!', 400

    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()
    user = Users.query.filter_by(id=user_id).first()

    if not user:
        return 'Brak takiego użytkownika.', 404
    elif user.id == 1:
        return 'Nie można zmieniać poziomu admina RCON!', 403
    elif not re.match("^[0-4]*$", is_admin):
        return 'Podano błędny poziom admina.', 400
    elif int(user.admin) >= int(you.admin):
        return 'Twój poziom admina musi być większy niż użytkownika.', 403
    elif int(you.admin) <= int(is_admin):
        return 'Twój poziom admina musi być większy niż chcesz ustawić!', 403

    if is_admin == '1':
        if user.vip_date is None:
            today = datetime.datetime.now()
            vip_date = today + datetime.timedelta(days=days)
            user.vip_date = vip_date
        else:
            vip_date = user.vip_date + datetime.timedelta(days=days)
            user.vip_date = vip_date
    else:
        user.vip_date = None

    user.admin = is_admin

    db.session.commit()
    return f'Użytkownik {user.username} ma teraz poziom admina: {user.admin}!', 200


@admin.route("/<user_id>/delete", methods=['post'])
@Auth.logged_admin
def _delete_(user_id):
    user = Users.query.filter_by(id=user_id).first()
    your_id = session.get("user_id")
    you = Users.query.filter_by(id=your_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return 'Brak takiego użytkownika.', 404
    elif user_id == "1":
        return 'Nie można banować i usuwać RCON admina!', 403
    elif int(user.admin) >= int(you.admin):
        return 'Twój poziom admina musi być większy niż użytkownika.', 403

    post = request.get_json()
    days = post.get("days")

    try:
        time = int(days)
    except ValueError:
        return 'Wprowadzona wartość nie jest liczbą.', 400

    if time == 0:
        user.ban_date = None
        alert = f'Odbanowałeś gracza {user.username}!'
    elif 0 < time < 366:
        today = datetime.datetime.now()
        ban = today + datetime.timedelta(days=time)
        user.ban_date = ban
        alert = f'Zbanowałeś gracza {user.username} na {time} dni!'
    elif time == 2580:
        Posts.query.filter_by(owner_id=user_id).delete()
        Postsa.query.filter_by(owner_id=user_id).delete()
        Postsm.query.filter_by(owner_id=user_id).delete()
        Postsv.query.filter_by(owner_id=user_id).delete()
        Postsnews.query.filter_by(owner_id=user_id).delete()
        Postsbugs.query.filter_by(owner_id=user_id).delete()
        Postssug.query.filter_by(owner_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
        alert = f'Usunołeś użytkownika {user.username}!'
    else:
        return 'Wprowadz liczbę dni od 0 - 365 lub kod usuwania.', 400
    db.session.commit()
    return alert, 200
