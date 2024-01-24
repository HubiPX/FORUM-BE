from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import timedelta
from blueprints.login import login
from blueprints.admin import admin
from blueprints.game import game
from blueprints.shop import shop
from blueprints.logout import logout
from blueprints.users import users
from blueprints.info import info
from posts.posts import posts
from posts.postsadmin import postsa
from posts.postsmod import postsm
from posts.postsvip import postsv
from posts.postsnews import postsnews
from posts.postsbugs import postsbugs
from posts.postssug import postssug
from database.models import db, Users
from database.hash import Hash
from flask_cors import CORS

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=7)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
CORS(app, supports_credentials=True, origins="http://127.0.0.1:5500")
app.config.from_object('database.config.Config')

socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5500")

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

with app.app_context():
    db.app = app
    db.init_app(app)
    db.create_all()

    if Users.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first() is None:
        pwd = Hash.hash_password(DEFAULT_ADMIN_PASSWORD)
        admin_account = Users(username=DEFAULT_ADMIN_USERNAME, password=pwd, admin=4)
        db.session.add(admin_account)
        db.session.commit()

app.register_blueprint(login, url_prefix='/api/login')
app.register_blueprint(logout, url_prefix='/api/logout')
app.register_blueprint(users, url_prefix='/api/users')
app.register_blueprint(info, url_prefix='/api/info')
app.register_blueprint(posts, url_prefix='/api/posts')
app.register_blueprint(postsa, url_prefix='/api/postsa')
app.register_blueprint(postsm, url_prefix='/api/postsm')
app.register_blueprint(postsv, url_prefix='/api/postsv')
app.register_blueprint(postsnews, url_prefix='/api/postsnews')
app.register_blueprint(postsbugs, url_prefix='/api/postsbugs')
app.register_blueprint(postssug, url_prefix='/api/postssug')
app.register_blueprint(admin, url_prefix='/api/admin')
app.register_blueprint(game, url_prefix='/api/game')
app.register_blueprint(shop, url_prefix='/api/shop')

if __name__ == "__main__":
    app.debug = True
    socketio.run(app, port=4400, allow_unsafe_werkzeug=True)
