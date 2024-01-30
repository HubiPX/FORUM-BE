import math
from flask import Blueprint, session, request
from blueprints.auth import Auth
from database.models import Postsbugs, Users
from database.models import db
import datetime

postsbugs = Blueprint('postsbugs', __name__)


@postsbugs.route('/create', methods=['post'])
@Auth.logged_user
def create_post():
    user_id = session.get("user_id")
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść posta.', 400

    today = datetime.datetime.now()

    post = Postsbugs(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.postsbugs.append(post)
    db.session.commit()
    return '', 201


@postsbugs.route('all/<page_nr>', methods=['get'])
@Auth.logged_user
def get_all_posts(page_nr):
    page_nr = int(page_nr)

    x = 10
    pages = math.ceil(db.session.query(Postsbugs).count() / x)

    if pages < page_nr < 1:
        return ''

    offset = (page_nr - 1) * x  # ile trzeba pominąć
    posts = db.session.query(Postsbugs, Users).join(Postsbugs).order_by(Postsbugs.id.desc()).offset(offset).limit(x)

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


@postsbugs.route('/<post_id>/delete', methods=['get'])
@Auth.logged_user
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Postsbugs.query.filter_by(id=post_id).first():
            return 'Brak posta o tym ID.', 404
    else:
        if not Postsbugs.query.filter_by(owner_id=user.id, id=post_id).first():
            return 'Brak posta o tym ID, którego jesteś właścicielem.', 404

    Postsbugs.query.filter_by(id=post_id).delete()
    db.session.commit()
    return '', 200


@postsbugs.route('/<post_id>/edit', methods=['post'])
@Auth.logged_user
def edit_post(post_id):
    user_id = session.get("user_id")
    data = request.get_json()

    new_content = data.get("content")

    post = Postsbugs.query.filter_by(id=post_id, owner_id=user_id).first()

    if not post:
        return 'Brak takiego posta.', 404
    elif new_content == '':
        return 'Nowa treść posta jest pusta.', 204
    elif len(new_content) < 4:
        return 'Nowa treść posta jest za krótka.', 400

    post.content = new_content
    db.session.commit()
    return '', 201


@postsbugs.route('/search', methods=['post'])
@Auth.logged_user
def search_content():
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść.', 400

    all_posts = db.session.query(Postsbugs, Users).join(Postsbugs)
    print_posts = []

    for post, user in all_posts:
        if content.lower() in post.content.lower():
            print_posts.append({
                "user": user.username,
                "admin": user.admin,
                "color_nick": user.color_nick,
                "rank": user.rank,
                "id": post.id,
                "content": post.content,
                "date": post.date
            })
    print_posts = print_posts[::-1]
    print_posts.append(1)
    return print_posts
