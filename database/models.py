from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    posts = db.relationship("Posts")
    postsa = db.relationship("Postsa")
    postsm = db.relationship("Postsm")
    postsv = db.relationship("Postsv")
    postsnews = db.relationship("Postsnews")
    postsbugs = db.relationship("Postsbugs")
    postssug = db.relationship("Postssug")
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(192), nullable=False)
    admin = db.Column(db.Integer, primary_key=False)
    ban_date = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, primary_key=False)
    ranking = db.Column(db.Integer, primary_key=False)
    last_login = db.Column(db.DateTime, nullable=True)
    secret_numbers = db.Column(db.String(20), nullable=True)
    game = db.Column(db.String(30), nullable=True)
    game_info = db.Column(db.String(30), nullable=True)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postsa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postsm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postsv(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postsnews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postsbugs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)


class Postssug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, nullable=False)
