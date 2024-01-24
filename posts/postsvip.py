import math
from flask import Blueprint, session, request
from blueprints.auth import Auth
from database.models import Postsv, Users
from database.models import db
import datetime

postsv = Blueprint('postsv', __name__)


@postsv.route('/create', methods=['post'])
@Auth.logged_vip
def create_post():
    user_id = session.get("user_id")
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść posta.', 400

    today = datetime.datetime.now()

    post = Postsv(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.postsv.append(post)
    db.session.commit()
    return '', 201


@postsv.route('', methods=['get'])
@Auth.logged_vip
def get_my_posts():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    user_posts = user.postsv
    my_posts = []

    for x in user_posts:
        my_posts.append({
            "id": x.id,
            "content": x.content,
            "date": x.date
        })
    return my_posts


@postsv.route('all/<page_nr>', methods=['get'])
@Auth.logged_vip
def get_all_posts(page_nr):
    page_nr = int(page_nr)

    volume = 10
    pages = math.ceil(db.session.query(Postsv).count() / volume)

    if pages < page_nr < 1:
        return ''

    offset = (page_nr - 1) * volume  # ile trzeba pominąć
    posts = db.session.query(Postsv, Users).join(Postsv).order_by(Postsv.id.desc()).offset(offset).limit(volume)

    print_posts = []
    for post, user in posts:
        print_posts.append({
            "user": user.username,
            "admin": user.admin,
            "color_nick": user.color_nick,
            "rank": user.rank,
            "id": post.id,
            "content": post.content,
            "date": post.date
        })

    print_posts.append(pages)
    return print_posts


@postsv.route('/<post_id>/delete', methods=['get'])
@Auth.logged_vip
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Postsv.query.filter_by(id=post_id).first():
            return 'Brak posta o tym ID.', 404
    else:
        if not Postsv.query.filter_by(owner_id=user.id, id=post_id).first():
            return 'Brak posta o tym ID, którego jesteś właścicielem.', 404

    Postsv.query.filter_by(id=post_id).delete()
    db.session.commit()
    return '', 200


@postsv.route('/<post_id>/edit', methods=['post'])
@Auth.logged_vip
def edit_post(post_id):
    user_id = session.get("user_id")
    data = request.get_json()

    new_content = data.get("content")

    post = Postsv.query.filter_by(id=post_id, owner_id=user_id).first()

    if not post:
        return 'Brak takiego posta.', 404
    elif new_content == '':
        return 'Nowa treść posta jest pusta.', 204
    elif len(new_content) < 4:
        return 'Nowa treść posta jest za krótka.', 400

    post.content = new_content
    db.session.commit()
    return '', 201
