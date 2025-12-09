from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    from app.config import config

    app.config.from_object(config)

    # Session configuration
    app.config["SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = False

    CORS(app)

    # Register API blueprint
    from app.api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Register web blueprint
    from app.web.routes import web_bp

    app.register_blueprint(web_bp)

    return app
