import flask
from datetime import datetime, timedelta
from website import models, forms
from website.views.account import isLoggedIn, logout
from ipaddress import ip_address

app = flask.current_app
bp = flask.Blueprint('main', __name__)


@bp.app_errorhandler(404)
def page_not_found(e):
    return flask.render_template('errors/404.html'), 404


@bp.before_app_request
def before_request():
    flask.g.user = None
    if 'user_id' in flask.session:
        user = models.User.by_id(flask.session['user_id'])
        if not user:
            return logout()

        flask.g.user = user
        
        if 'timeout' not in flask.session or flask.session['timeout'] < datetime.now():
            flask.session['timeout'] = datetime.now() + timedelta(days=7)
            flask.session.permanent = True
            flask.session.modified = True
            models.User.update_last_login(user.id, {'last_login_date': datetime.utcnow(), 'last_login_ip': ip_address(flask.request.remote_addr).packed})


@bp.app_template_filter('timeformatted')
def _jinja_datetime(date, format='%d/%b/%Y'):
    return date.strftime(format)



def isMobile():
    ua = flask.request.user_agent
    return ua.platform == 'iphone' or ua.platform == 'android' or ua.platform == 'ipad'


@bp.route('/home')
@bp.route('/')
def home():
    return flask.render_template('pages/index.html', loggedin=isLoggedIn())
