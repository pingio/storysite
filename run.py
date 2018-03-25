from website import create_app
import config
if __name__ == "__main__":
    app = create_app('config')
    app.run(host=config.SITE_URL, port=config.SITE_PORT, debug=config.DEBUG)
