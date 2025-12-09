from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    from app.config import config

    app.config.from_object(config)

    CORS(app)

    from app.api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app
