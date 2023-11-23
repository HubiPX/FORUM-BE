from flask import Blueprint, request, session, redirect
from database.models import db
from database.models import Users
from blueprints.auth import Auth
import datetime
import stripe


shop = Blueprint('shop', __name__)
stripe.api_key = 'sk_test_51ODP5ODGF0Nh3vajmnOnK05aTVkCCnNSmQdZB4e8KB1OWm6GBtzQFZixUvE4NH8rPJoYNGDkbCWSXSXn32nxVZoA006OF1HFMn'
YOUR_DOMAIN = 'http://localhost:4400'


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

    if option == 1 and user.admin <= 1:
        if user.vip_date is None:
            vip_date = today + datetime.timedelta(days=time)
            user.vip_date = vip_date
            user.admin = 1
        else:
            vip_date = user.vip_date + datetime.timedelta(days=time)
            user.vip_date = vip_date
    elif option == 2:
        user.score = x + score
    elif 3 <= option <= 5 and (color_nick == 0 or user.color_nick == (option - 2)) and x >= score and user.admin == 0:
        if user.cnick_date is None:
            user.color_nick = option - 2
            user.cnick_date = today + datetime.timedelta(days=time)
            user.score = x - score
        else:
            cnick_date = user.cnick_date + datetime.timedelta(days=time)
            user.cnick_date = cnick_date
    elif 6 <= option <= 8 and (rank == 0 or user.rank == (option - 5)) and x >= score and user.admin == 0:
        if user.rank_date is None:
            user.rank = option - 5
            user.rank_date = today + datetime.timedelta(days=time)
            user.score = x - score
        else:
            rank_date = user.rank_date + datetime.timedelta(days=time)
            user.rank_date = rank_date
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


@shop.route('/webhook', methods=['POST'])
def stripe_webhook():
    print('płatność')
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'twój_endpoint_stripe_secret'
        )
    except ValueError as e:
        print("Invalid payload")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        return 'Invalid signature', 400

    # Obsługa różnych typów zdarzeń (event)
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # Obiekt udanej transakcji
        print('Płatność udana:', payment_intent)

        # Tutaj możesz dodać kod reagujący na udaną płatność

    return '', 200


@shop.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Podaj dokładne ID ceny produktu, który chcesz sprzedać
                    'price': 'price_1ODPFGDGF0Nh3vajTMN8lnEf',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)
