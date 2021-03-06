"""Main application and routing logic for TweetCompare."""
import os
from os import getenv
from pickle import dump, loads
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user, display_user_tweets, add_users
from .predict import predict_user
from decouple import config


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
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

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted((request.values['user1'],
                               request.values['user2']))
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            comparison = predict_user(user1, user2,
                                      request.values['tweet_text'])
            user1_name = comparison.user1_name
            user2_name = comparison.user2_name
            user1_prob = comparison.user1_prob
            user2_prob = comparison.user2_prob
            prediction = comparison.predicted_user
            message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'],
                user1_name if prediction else user2_name,
                user2_name if prediction else user1_name)
        return render_template('prediction.html', title='Prediction',
                               message=message,
                               user1_name=user1_name, user1_prob=user1_prob,
                               user2_name=user2_name, user2_prob=user2_prob
                               )

    @app.route('/reset')
    def reset():
        # CACHE.flushall()
        # CACHED_COMPARISONS.clear()
        DB.drop_all()
        DB.create_all()
        add_users()
        return render_template('base.html', title='Reset database!')
    return app
