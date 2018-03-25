from flask import g, request, url_for, redirect, session, render_template, make_response, current_app, Blueprint

from website import models, forms
from website.extensions import db

app = current_app
bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def home():
    return 'test'

