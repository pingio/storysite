from website.views import (
    main,
    story,
    user,
    account,
    admin,
)


def registerBlueprints(flask_app):
    flask_app.register_blueprint(main.bp)
    flask_app.register_blueprint(story.bp)
    flask_app.register_blueprint(user.bp)
    flask_app.register_blueprint(account.bp)
    flask_app.register_blueprint(admin.bp)
