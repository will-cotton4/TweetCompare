"""Main application and routing logic for TweetCompare."""
from os import getenv
from pickle import dump, loads
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from decouple import config


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = config('ENV')
    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    return app
