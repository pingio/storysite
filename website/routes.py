import uuid
import base64
import json

from website import app, db
from flask import render_template, abort, request, redirect, url_for, session, g, make_response
from website import forms, models
from datetime import datetime, timedelta


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = models.User.by_id(session['user_id'])
        if not user:
            return logout()

        g.user = user

        if 'timeout' not in session or session['timeout'] < datetime.now():
            session['timeout'] = datetime.now() + timedelta(days=7)
            session.permanent = True
            session.modified = True


@app.template_filter('timeformatted')
def _jinja_datetime(date, format='%d/%b/%Y'):
    return date.strftime(format)

def isMobile():
    ua = request.user_agent
    return ua.platform == 'iphone' or ua.platform == 'android' or ua.platform == 'ipad'

def isLoggedIn():
    return g.user is not None


def redirect_url():
    url = request.args.get('next') or \
        request.referrer or \
        '/'
    if url == request.url:
        return '/'
    return url

# routes start here

@app.route('/home')
@app.route('/')
def index():
    return render_template('pages/index.html', loggedin=isLoggedIn())


@app.route('/list', defaults={'extra': None})
@app.route('/list/<extra>')
def list(extra=None):
    if not isMobile():
        stories = models.Story.get_list()
        if extra is not None:
            extra = extra.lower()
            if extra != 'top' and extra != 'latest' and extra != 'alphabetical':
                return abort(404)
        return render_template('pages/list.html', sort=extra, result=stories, loggedin=isLoggedIn())


@app.route('/story/<url>')
def story(url):
    story = models.Story.by_url(url)

    if story:
        return render_template('pages/story.html', info=story, loggedin=isLoggedIn())
    return abort(404)


@app.route('/story/<url>/comments', methods=['GET', 'POST'])
def story_comments(url):
    form = forms.CommentForm(request.form)
    if request.method == 'GET':
        story = models.Story.by_url(url)
        comments = models.Comment.by_url(url)

        if not comments:
            return abort(404)
                    
        return render_template('pages/comments.html', story=story, comments=comments, url=url, form=form, loggedin=isLoggedIn())

    if request.method == 'POST' and form.validate():
        comment = models.Comment(
            story = url,
            author = g.user.username,
            parent_comment = None,
            comment = form.comment.data
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('story_comments', url=url))

@app.route('/story/<url>/reviews', methods=['GET', 'POST'])
def story_revies(url):
    form = forms.ReviewForm(request.form)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if g.user == None:
        return redirect(url_for('login'))
    form = forms.SubmitForm(request.form)
    if request.method == 'POST' and form.validate():
        url = base64.urlsafe_b64encode(uuid.uuid1().bytes)[:5]
        story = models.Story(
            url=url, 
            author=g.user.username, 
            title=form.title.data.strip(), 
            synopsis=form.synopsis.data.strip(), 
            story=form.story.data
            )
        db.session.add(story)
        db.session.commit()
        return redirect(url_for('story', url=url))
    return render_template('pages/submit.html', form=form, loggedin=isLoggedIn())


@app.route('/account')
def account():
    if not isLoggedIn():
        return redirect('login')

    userinfo = models.User.by_username(g.user.username)
    storyLen = models.Story.count_by_username(g.user.username)
    return render_template('pages/account.html', user=userinfo, storylen=storyLen, loggedin=True)

@app.route('/admin')
def admin():
    if not models.isLoggedIn() or g.user.rank is not models.UserRank.ADMIN:
        return "not admin"
    
    return "admin"


@app.route('/account/settings')
def account_settings():
    return redirect('account')

@app.route('/account/stories')
def account_stories():
    userinfo = models.User.by_username(g.user.username)
    stories = models.Story.list_by_username(g.user.username)
    storyLen = models.Story.count_by_username(g.user.username)

    return render_template('pages/user.html', user=userinfo, stories=stories, storylen=storyLen, accountSettings=True, loggedin=isLoggedIn())


@app.route('/user/<username>')
def user(username):
    userinfo = models.User.by_username(username)

    if userinfo:
        stories = models.Story.list_by_username(username)
        storyLen = models.Story.count_by_username(username)
        return render_template('pages/user.html', user=userinfo, stories=stories, storylen=storyLen, loggedin=isLoggedIn())
    return abort(404)


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(redirect_url())

    form = forms.LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data.strip()
        password = form.password.data

        user = models.User.by_username(username)
        if (not user or password != user.password.join(user.salt)):
            return redirect(url_for('login', error='valfail'))

        db.session.add(user)
        db.session.commit()

        g.user = user
        session['user_id'] = user.id
        session.permanent = True
        session.modified = True
        return redirect(redirect_url())

    return render_template('pages/login.html', form=form, loggedin=isLoggedIn(), error=request.args.get('error'))


@app.route('/account/signup', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for('index'))

    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        salt = models.generateSalt()
        user = models.User(username=form.username.data.strip(),
                           password=form.password.data,
                           salt=salt)
        db.session.add(user)
        db.session.commit()

        g.user = user
        session['user_id'] = user.id
        session.permanent = True
        session.modified = True
        return redirect(url_for('index'))

    return render_template('pages/signup.html', form=form, loggedin=isLoggedIn())


@app.route('/logout')
def logout():
    g.user = None
    session.permanent = False
    session.modified = False

    response = make_response(redirect(redirect_url()))
    response.set_cookie(app.session_cookie_name, expires=0)
    return response
