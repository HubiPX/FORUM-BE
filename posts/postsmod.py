import math
from flask import Blueprint, session, request
from blueprints.auth import Auth
from database.models import Postsm, Users
from database.models import db
import datetime

postsm = Blueprint('postsm', __name__)


@postsm.route('/create', methods=['post'])
@Auth.logged_mod
def create_post():
    user_id = session.get("user_id")
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść posta.', 400

    today = datetime.datetime.now()

    post = Postsm(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.postsm.append(post)
    db.session.commit()
    return '', 201


@postsm.route('', methods=['get'])
@Auth.logged_mod
def get_my_posts():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    user_posts = user.postsm
    my_posts = []

    for x in user_posts:
        my_posts.append({
            "id": x.id,
            "content": x.content,
            "date": x.date
        })
    return my_posts


@postsm.route('all/<page_nr>', methods=['get'])
@Auth.logged_mod
def get_all_posts(page_nr):
    page_nr = int(page_nr)
    pages = math.ceil(db.session.query(Postsm).count() / 10)

    if pages < page_nr < 1:
        return ''
    all_posts = db.session.query(Postsm, Users).join(Postsm)
    all_posts = all_posts[::-1]
    print_posts = []

    for post, user in all_posts[((page_nr-1) * 10):page_nr*10]:
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


@postsm.route('/<post_id>/delete', methods=['get'])
@Auth.logged_mod
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Postsm.query.filter_by(id=post_id).first():
            return 'Brak posta o tym ID.', 404
    else:
        if not Postsm.query.filter_by(owner_id=user.id, id=post_id).first():
            return 'Brak posta o tym ID, którego jesteś właścicielem.', 404

    Postsm.query.filter_by(id=post_id).delete()
    db.session.commit()
    return '', 200


@postsm.route('/<post_id>/edit', methods=['post'])
@Auth.logged_mod
def edit_post(post_id):
    user_id = session.get("user_id")
    data = request.get_json()

    new_content = data.get("content")

    post = Postsm.query.filter_by(id=post_id, owner_id=user_id).first()

    if not post:
        return 'Brak takiego posta.', 404
    elif new_content == '':
        return 'Nowa treść posta jest pusta.', 204
    elif len(new_content) < 4:
        return 'Nowa treść posta jest za krótka.', 400

    post.content = new_content
    db.session.commit()
    return '', 201
