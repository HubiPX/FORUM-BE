from flask import Blueprint, request
from database.models import db
from database.models import Users
from blueprints.auth import Auth
import datetime

shop = Blueprint('shop', __name__)


@shop.route("/<user_id>/buy", methods=['post'])
@Auth.logged_user
def _buy_(user_id):
    user = Users.query.filter_by(id=user_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return '', 404

    post = request.get_json()
    score = int(post.get("score"))
    option = int(post.get("option"))
    time = int(post.get("time"))

    x = user.score
    color_nick = user.color_nick
    rank = user.rank
    today = datetime.datetime.now()

    if option == 1:
        if user.vip_date is None:
            vip_date = today + datetime.timedelta(days=time)
            user.vip_date = vip_date
            user.admin = 1
        else:
            vip_date = user.vip_date + datetime.timedelta(days=time)
            user.vip_date = vip_date
    elif option == 2:
        user.score = x + score
    elif 3 <= option <= 5 and color_nick == 0 and x >= -score:
        user.color_nick = option
        user.cnick_date = today + datetime.timedelta(days=time)
        user.score = x + score
    elif 6 <= option <= 8 and rank == 0 and x >= -score:
        user.rank = option
        user.rank_date = today + datetime.timedelta(days=time)
        user.score = x + score
    else:
        return '', 400

    db.session.commit()
    return '', 200
