import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Are we doing debugging?
DEBUG = True
USE_MYSQL = True

# Site stuff
SITE_NAME = 'Libstories'
SITE_URL = 'localhost'
SITE_PORT = 5555

if USE_MYSQL:
    SQLALCHEMY_DATABASE_URI = (
        'mysql://root:123456@localhost/storysite')
else:
    SQLALCHEMY_DATABASE_URI = (
        'sqlite:///' + os.path.join(BASE_DIR, 'test.db') + '?check_same_thread=False')

TABLE_USERS = 'users'
TABLE_STORIES = 'stories'
TABLE_COMMENTS = 'comments'
TABLE_REVIEWS = 'reviews'

# Security
SECRET_KEY = '*******'
