from flask import g, request, url_for, redirect, session, render_template, make_response, current_app, Blueprint, abort

from website import models, forms
from website.extensions import db
from website.views.main import isMobile
from website.views.account import isLoggedIn, redirect_url

import base64
import uuid

app = current_app
bp = Blueprint('story', __name__, url_prefix='/story')


@bp.route('/list', defaults={'extra': None})
@bp.route('/list/<extra>')
def list(extra=None):
    if not isMobile():
        stories = models.Story.get_list()
        if extra is not None:
            extra = extra.lower()
            if extra != 'top' and extra != 'latest' and extra != 'alphabetical':
                return abort(404)
        return render_template('pages/list.html', sort=extra, result=stories, loggedin=isLoggedIn())


@bp.route('/read/<url>')
def read(url):
    story = models.Story.by_url(url)

    if story:
        return render_template('pages/story.html', info=story, loggedin=isLoggedIn())
    return abort(404)


@bp.route('/read/<url>/comments', methods=['GET', 'POST'])
def comments(url):
    form = forms.CommentForm(request.form)
    if request.method == 'GET':
        story = models.Story.by_url(url)
        comments = models.Comment.by_url(url)

        if not comments:
            return abort(404)

        return render_template('pages/comments.html', story=story, comments=comments, url=url, form=form, loggedin=isLoggedIn())

    if request.method == 'POST' and form.validate():
        comment = models.Comment(
            story=url,
            author=g.user.username,
            parent_comment=None,
            comment=form.comment.data
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('story_comments', url=url))


@bp.route('/read/<url>/reviews', methods=['GET', 'POST'])
def reviews(url):
    form = forms.ReviewForm(request.form)


@bp.route('/submit', methods=['GET', 'POST'])
def submit():
    if g.user == None:
        return redirect(url_for('account.login'))
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
        return redirect(url_for('story.read', url=url))
    return render_template('pages/submit.html', form=form, loggedin=isLoggedIn())
