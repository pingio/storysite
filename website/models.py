import flask
import datetime
import random

from website.extensions import db, config


from enum import IntEnum, Enum

from sqlalchemy_utils import PasswordType, ChoiceType

from werkzeug.security import generate_password_hash, check_password_hash

app = flask.current_app

def generateSalt():
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    
    return "".join(chars)


class UserRank(IntEnum):
    NORMAL = 0
    VIP = 1
    ADMIN = 2

class User(db.Model):
    
    __tablename__ = config['TABLE_USERS']

    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(PasswordType(max_length=255, schemes=['bcrypt']), nullable=False)
    salt = db.Column(db.String(16), nullable=False)

    rank = db.Column(ChoiceType(UserRank, impl=db.Integer()), nullable=False, default=UserRank.NORMAL)
    created_time = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)

    last_login_date = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow, nullable=True)
    last_login_ip = db.Column(db.Binary(length=16), default=None, nullable=True)

    def __init__(self, username, password, salt, last_ip):
        self.username = username
        self.password = password.join(salt)
        self.salt = salt
        self.last_login_ip = last_ip

    def __repr__(self):
        return '<User %r>' % self.username

    def validate_authorization(self, password):
        ''' Returns a boolean for whether the user can be logged in '''
        checks = [
            # Password must match
            password == self.password
            # Reject inactive and banned users
        ]
        return all(checks)

    @classmethod
    def by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def by_username(cls, username):
        user = cls.query.filter_by(username=username).first()
        return user

    @classmethod
    def update_last_login(cls, id, update):
        cls.query.filter_by(id=id).update(update)


class Story(db.Model):
    __tablename__ = config['TABLE_STORIES']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(10), unique=True, nullable=False)
    author = db.Column(db.String(100), index=True, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    story = db.Column(db.Text, nullable=False)
    synopsis = db.Column(db.String(255), nullable=False)
    votes = db.Column(db.Integer, nullable=False, autoincrement=False)

    def __init__(self, url, author, title, story, synopsis):
        self.url = url
        self.author = author
        self.title = title
        self.story = story
        self.synopsis = synopsis
        self.votes = 0

    def __repr__(self):
        return '<Story %r>' % self.url

    @classmethod
    def by_url(cls, url):
        story = cls.query.filter_by(url=url).first()
        return story

    @classmethod
    def list_by_username(cls, username):
        stories = cls.query.filter_by(author=username)
        return stories

    @classmethod
    def count_by_username(cls, username):
        count = cls.query.filter_by(author=username).count()
        return count

    @classmethod
    def get_list(cls):
        stories = cls.query.all()
        return stories

    @classmethod
    def delete_by_username(cls, username):
        cls.query.filter_by(author=username).delete()


class Comment(db.Model):
    __tablename__ = config['TABLE_COMMENTS']
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    story = db.Column(db.String(10), index=True, nullable=False)
    author = db.Column(db.String(100), index=True, nullable=False)
    parent_comment = db.Column(db.Integer, db.ForeignKey(__tablename__+'.id'))
    comment = db.Column(db.Text, nullable=False)
    children = db.relationship('Comment')

    def __repr__(self):
        return '<Story %r>' % self.url

    @classmethod
    def by_url(cls, url):
        comments = cls.query.filter_by(story=url)
        return comments
    

class Review(db.Model):
    __tablename__ = config['TABLE_REVIEWS']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    story = db.Column(db.String(10), index=True, nullable=False)
    author = db.Column(db.String(100), index=True, nullable=False)
    score = db.Column(db.Integer, index=True, nullable=False)
    review = db.Column(db.Integer, index=True, nullable=False)
