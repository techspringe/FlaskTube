"""
Create Application
"""

from flask import Flask
from FlaskTube.config import LocalConfig, ProductionConfig


def create_app():
    """
    return app context
    """
    app = Flask(__name__)
    app.config.from_object(LocalConfig)
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    return app


from FlaskTube.main.views import main
from FlaskTube.api.routes import api
