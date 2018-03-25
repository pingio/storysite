from flask import g, request, url_for, redirect, session, render_template, make_response, current_app, Blueprint, abort, jsonify

from website import models, forms
from website.extensions import db
import uuid
import sys
from datetime import datetime
from ipaddress import ip_address

app = current_app
bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/')
def home():
    if not isLoggedIn():
        return redirect(url_for('account.login'))

    userinfo = models.User.by_username(g.user.username)
    storyLen = models.Story.count_by_username(g.user.username)
    return render_template('pages/account.html', user=userinfo, storylen=storyLen)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(redirect_url())

    form = forms.LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data.strip()
        password = form.password.data

        user = models.User.by_username(username)
        if (not user or password.join(user.salt) != (user.password)):
            return redirect(url_for('account.login', error='valfail'))

        user.last_login_date = datetime.utcnow()
        user.last_login_ip = ip_address(request.remote_addr).packed

        db.session.add(user)
        db.session.commit()

        g.user = user
        session['user_id'] = user.id
        session.permanent = True
        session.modified = True
        return redirect(redirect_url())

    return render_template('pages/login.html', form=form, error=request.args.get('error'))


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for(redirect_url()))

    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        salt = models.generateSalt()
        user = models.User(username=form.username.data.strip(),
                           password=form.password.data,
                           salt=salt,
                           last_ip = ip_address(request.remote_addr).packed)
        db.session.add(user)
        db.session.commit()

        g.user = user
        session['user_id'] = user.id
        session.permanent = True
        session.modified = True
        return redirect(url_for('main.home'))

    return render_template('pages/signup.html', form=form)


@bp.route('/logout')
def logout():
    g.user = None
    session.permanent = False
    session.modified = False
    
    response = make_response(redirect(url_for('main.home')))
    response.set_cookie(app.session_cookie_name, expires=0)
    return response


@bp.route('/delete')
@bp.route('/delete/<username>')
@bp.route('/delete/<username>/<token>', methods=['POST'])
def delete(username = None, token = None):
    if g.user == None or username != g.user.username:
        abort(404)
        return
    # Update this to its own table in db
    if token is None:
        tempTok = uuid.uuid4().hex
        session['delete_token'] = tempTok
        return jsonify(tempTok)

    if token is not None and 'delete_token' not in session:
        abort(403)
        return

    if token is not None and 'delete_token' in session and g.user.username == username:
        if token != session['delete_token']:
            abort(403)
            return
        
        user = models.User.by_username(g.user.username)
        models.Story.delete_by_username(g.user.username)
        db.session.delete(user)
        db.session.commit()

        return redirect(url_for('account.logout'))

    return redirect(redirect_url())



@bp.route('/settings')
def settings():
    userinfo = models.User.by_username(g.user.username)
    storyLen = models.Story.count_by_username(g.user.username)
    last_ip += "{0}".format(ip_address(userinfo.last_login_ip))

    return render_template('pages/account.html', user=userinfo, storylen=storyLen, last_ip = ip)


@bp.route('/stories')
def stories():
    userinfo = models.User.by_username(g.user.username)
    stories = models.Story.list_by_username(g.user.username)
    storyLen = models.Story.count_by_username(g.user.username)

    return render_template('pages/account.html', user=userinfo, stories=stories, storylen=storyLen)



def redirect_url():
    home_url = url_for('main.home')

    url = request.args.get('next') or \
        request.referrer or \
        home_url
    if url == request.url:
        return home_url

    return url


def isLoggedIn():
    return g.user is not None
