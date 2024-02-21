import math
from flask import Blueprint, session, request
from blueprints.auth import Auth
from database.models import Postssug, Users
from database.models import db
import datetime

postssug = Blueprint('postssug', __name__)


@postssug.route('/create', methods=['post'])
@Auth.logged_user
def create_post():
    user_id = session.get("user_id")
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść posta.', 400

    today = datetime.datetime.now()

    post = Postssug(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.postssug.append(post)
    db.session.commit()
    return '', 201


@postssug.route('all/<page_nr>', methods=['get'])
@Auth.logged_user
def get_all_posts(page_nr):
    page_nr = int(page_nr)

    x = 20
    pages = math.ceil(db.session.query(Postssug).count() / x)

    if pages < page_nr < 1:
        return ''

    offset = (page_nr - 1) * x  # ile trzeba pominąć
    posts = db.session.query(Postssug, Users).join(Postssug).order_by(Postssug.id.desc()).offset(offset).limit(x)

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


@postssug.route('/<post_id>/delete', methods=['get'])
@Auth.logged_user
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Postssug.query.filter_by(id=post_id).first():
            return 'Brak posta o tym ID.', 404
    else:
        if not Postssug.query.filter_by(owner_id=user.id, id=post_id).first():
            return 'Brak posta o tym ID, którego jesteś właścicielem.', 404

    Postssug.query.filter_by(id=post_id).delete()
    db.session.commit()
    return '', 200


@postssug.route('/<post_id>/edit', methods=['post'])
@Auth.logged_user
def edit_post(post_id):
    user_id = session.get("user_id")
    data = request.get_json()

    new_content = data.get("content")

    post = Postssug.query.filter_by(id=post_id, owner_id=user_id).first()

    if not post:
        return 'Brak takiego posta.', 404
    elif new_content == '':
        return 'Nowa treść posta jest pusta.', 204
    elif len(new_content) < 4:
        return 'Nowa treść posta jest za krótka.', 400

    post.content = new_content
    db.session.commit()
    return '', 201


@postssug.route('/search', methods=['post'])
@Auth.logged_user
def search_content():
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return 'Za krótka treść.', 400

    all_posts = db.session.query(Postssug, Users).join(Postssug)
    print_posts = []

    for post, user in all_posts:
        post_content = post.content.lower()
        found_all_words = True
        for word in content.lower().split():  # Podział treści na wyrazy
            if word not in post_content:
                found_all_words = False
                break
        if found_all_words:
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
