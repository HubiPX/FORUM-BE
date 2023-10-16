from flask import Blueprint, session, request
from sqlalchemy import desc
from blueprints.auth import Auth
from database.models import Posts, Users
from database.models import Postsa, Postsbugs, Postsm, Postsnews, Postssug, Postsv
from database.models import db
import datetime

posts = Blueprint('posts', __name__)


@posts.route('/create', methods=['post'])
@Auth.logged_user
def create_post():
    user_id = session.get("user_id")
    post = request.get_json()

    content = post.get("content")

    if len(content) < 3:
        return '', 400

    today = datetime.datetime.now()

    post = Posts(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.posts.append(post)
    db.session.commit()
    return '', 201


@posts.route('', methods=['get'])
@Auth.logged_user
def get_my_posts():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    user_posts = user.posts
    my_posts = []

    for x in user_posts:
        my_posts.append({
            "id": x.id,
            "content": x.content,
            "date": x.date
        })
    return my_posts


@posts.route('all', methods=['get'])
def get_all_posts():
    all_posts = db.session.query(Posts, Users).join(Posts)
    print_posts = []
    today = datetime.datetime.now()

    for post, user in all_posts:
        if not ((post.date - today).total_seconds() / 3600) > 24:
            print_posts.append({
                "user": user.username,
                "admin": user.admin,
                "id": post.id,
                "content": post.content,
                "date": post.date
            })
        else:
            db.session.delete(post)
    return print_posts[::-1]


@posts.route('/<post_id>/delete', methods=['get'])
@Auth.logged_user
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Posts.query.filter_by(id=post_id).first():
            return '', 404
    else:
        if not Posts.query.filter_by(owner_id=user.id, id=post_id).first():
            return '', 404

    Posts.query.filter_by(id=post_id).delete()
    db.session.commit()
    return '', 200


@posts.route('/<post_id>/edit', methods=['post'])
@Auth.logged_user
def edit_post(post_id):
    user_id = session.get("user_id")
    data = request.get_json()

    new_content = data.get("content")

    post = Posts.query.filter_by(id=post_id, owner_id=user_id).first()

    if not post:
        return '', 404
    elif new_content == '':
        return '', 204
    elif len(new_content) < 4:
        return '', 400

    post.content = new_content
    db.session.commit()
    return '', 201


@posts.route('/quantity/<user_id>', methods=['get'])
@Auth.logged_user
def quantity(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return '', 400

    all_users = Users.query.order_by(desc(Users.score)).all()
    place = all_users.index(user) + 1
    "przypisanie do zmiennych ilości postów danego kanału"
    postsa = db.session.query(Postsa).count()
    postsm = db.session.query(Postsm).count()
    postsv = db.session.query(Postsv).count()
    postsnews = db.session.query(Postsnews).count()
    postssug = db.session.query(Postssug).count()
    postsbugs = db.session.query(Postsbugs).count()
    return {"postsa": postsa, "postsm": postsm, "postsv": postsv, "postsnews": postsnews,
            "postssug": postssug, "postsbugs": postsbugs, "place": place}
