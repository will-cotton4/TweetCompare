"""Main application and routing logic for TweetCompare."""
from os import getenv
from pickle import dump, loads
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user, display_user_tweets
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

    # TODO
    # @app.route('/update')
    # def update():
    #     if config('ENV') == 'production':
    #         CACHE.flushall()
    #         CACHED_COMPARISONS.clear()

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None,  message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} successfully added!".format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            return message
        else:
            return render_template('user.html', title=name, tweets=tweets,
                                   message=message)

    return app
