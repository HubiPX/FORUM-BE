from flask import Blueprint, request, session
from database.models import db
from database.models import Users
from blueprints.auth import Auth
import datetime

shop = Blueprint('shop', __name__)


@shop.route("/buy", methods=['post'])
@Auth.logged_user
def _buy_():
    if not Users.query.filter_by(id=session["user_id"]).first():
        return '', 404

    user = Users.query.filter_by(id=session["user_id"]).first()

    post = request.get_json()
    option = int(post.get("option"))
    time = int(post.get("time"))

    x = user.score
    color_nick = user.color_nick
    rank = user.rank
    today = datetime.datetime.now()

    prices = {
        1: {'7dni': 0, '30dni': 0, '180dni': 0},
        2: {'7dni': 1000, '30dni': 4000, '180dni': 10000},  # dni odpowiadają kolejno 1K 4K i 10K exp
        3: {'7dni': 300, '30dni': 1500, '180dni': 5000},
        4: {'7dni': 400, '30dni': 1750, '180dni': 6000},
        5: {'7dni': 500, '30dni': 2000, '180dni': 7500},
        6: {'7dni': 100, '30dni': 300, '180dni': 1000},
        7: {'7dni': 150, '30dni': 450, '180dni': 1500},
        8: {'7dni': 200, '30dni': 600, '180dni': 2000},
    }

    if option not in prices:
        return '', 400

    price_option = prices[option]

    if time == 7:
        score = price_option['7dni']
    elif time == 30:
        score = price_option['30dni']
    elif time == 180:
        score = price_option['180dni']
    else:
        return '', 400

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
    elif 3 <= option <= 5 and color_nick == 0 and x >= score and user.admin == 0:
        user.color_nick = option - 2
        user.cnick_date = today + datetime.timedelta(days=time)
        user.score = x - score
    elif 6 <= option <= 8 and rank == 0 and x >= score and user.admin == 0:
        user.rank = option - 5
        user.rank_date = today + datetime.timedelta(days=time)
        user.score = x - score
    elif x <= score:
        return '', 403
    else:
        return '', 400

    db.session.commit()
    return '', 200


@shop.route("/del", methods=['post'])
@Auth.logged_user
def _del_():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()

    if not Users.query.filter_by(id=user_id).first():
        return '', 404

    post = request.get_json()
    option = int(post.get("option"))

    if option == 1 and user.color_nick != 0:
        user.color_nick = 0
        user.cnick_date = None
    elif option == 2 and user.rank != 0:
        user.rank = 0
        user.rank_date = None
    else:
        return '', 400

    db.session.commit()
    return '', 200
