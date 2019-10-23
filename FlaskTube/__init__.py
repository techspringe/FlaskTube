"""
Create Application
"""

from flask import flask

def create_app():
    """
    return app context
    """
    app = Flask(__name__)

    return app
