from flask import Blueprint, request
from database.models import db
from database.models import Users
from blueprints.auth import Auth

shop = Blueprint('shop', __name__)


@shop.route("/<user_id>/store", methods=['post'])
@Auth.logged_user
def _store_(user_id):
    user = Users.query.filter_by(id=user_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return '', 404

    post = request.get_json()
    score = post.get("score")

    try:
        score = int(score)
    except ValueError:
        return '', 400

    if not 0 < score <= 10000:
        return '', 400

    x = user.score
    if x >= score:
        x = x - score
        user.score = x
    else:
        return '', 400

    db.session.commit()
    return '', 200