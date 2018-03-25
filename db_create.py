import sqlalchemy
from website import app, db, models

if __name__ == '__main__':
    database_empty = False
    try:
        models.User.query.first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError):
        database_empty = True

    print('Creating all tables...')
    db.create_all()
    print('Done!')