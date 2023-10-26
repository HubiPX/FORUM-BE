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
    shop_data = user.shop_data
    today = datetime.datetime.now()

    if option == 10:
        if user.vip_date is None:
            vip_date = today + datetime.timedelta(days=time)
            user.vip_date = vip_date
            user.admin = 1
        else:
            vip_date = user.vip_date + datetime.timedelta(days=time)
            user.vip_date = vip_date
    elif option == 11:
        user.score = x + score
    elif option <= 2 and shop_data[:3] == "000" and x >= -score:
        new_shop_data = user.shop_data[:option] + "1" + user.shop_data[option + 1:]
        user.shop_data = new_shop_data
        user.cnick_date = today + datetime.timedelta(days=time)
        user.score = x + score
    elif option >= 3 and shop_data[3:] == "000" and x >= -score:
        new_shop_data = user.shop_data[:option] + "1" + user.shop_data[option + 1:]
        user.shop_data = new_shop_data
        user.rank_date = today + datetime.timedelta(days=time)
        user.score = x + score
    else:
        return '', 400

    db.session.commit()
    return '', 200
