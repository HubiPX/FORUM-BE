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

    if len(content) < 4:
        return '', 400

    today = datetime.datetime.now()

    post = Postssug(content=content, date=today)
    user = Users.query.filter_by(id=user_id).first()

    user.postssug.append(post)
    db.session.commit()
    return '', 201


@postssug.route('', methods=['get'])
@Auth.logged_user
def get_my_posts():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    user_posts = user.postssug
    my_posts = []

    for x in user_posts:
        my_posts.append({
            "id": x.id,
            "content": x.content,
            "date": x.date
        })
    return my_posts[::-1]


@postssug.route('all', methods=['get'])
@Auth.logged_user
def get_all_posts():
    all_posts = db.session.query(Postssug, Users).join(Postssug)
    print_posts = []

    for post, user in all_posts:
        print_posts.append({
            "user": user.username,
            "admin": user.admin,
            "id": post.id,
            "content": post.content,
            "date": post.date
        })
    return print_posts[::-1]


@postssug.route('/<post_id>/delete', methods=['get'])
@Auth.logged_user
def delete_posts(post_id):
    user = Users.query.filter_by(id=session['user_id']).first()

    if user.admin:
        if not Postssug.query.filter_by(id=post_id).first():
            return '', 404
    else:
        if not Postssug.query.filter_by(owner_id=user.id, id=post_id).first():
            return '', 404

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
        return '', 404
    elif new_content == '':
        return '', 204
    elif len(new_content) < 4:
        return '', 400

    post.content = new_content
    db.session.commit()
    return '', 201
