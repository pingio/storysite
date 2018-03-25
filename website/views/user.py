from flask import g, request, url_for, redirect, session, render_template, make_response, current_app, Blueprint, abort

from website import models, forms
from website.extensions import db
from website.views.account import isLoggedIn

app = current_app
bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/')
def home():
    return redirect(url_for('main.home'))


@bp.route('/<username>')
def user(username):
    userinfo = models.User.by_username(username)

    if userinfo:
        stories = models.Story.list_by_username(username)
        storyLen = models.Story.count_by_username(username)
        return render_template('pages/user.html', user=userinfo, stories=stories, storylen=storyLen, loggedin=isLoggedIn())
    return abort(404)
