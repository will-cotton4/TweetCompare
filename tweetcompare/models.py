from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class User(DB.Model):
    """Twitter users that we pull and analyze Tweets for."""
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(15), nullable=False)
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '<USER {}>'.format(self.name)


class Tweet(DB.Model):
    """Tweets."""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(300))
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    embedding = DB.Column(DB.PickleType, nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return '<TWEET {}>'.format(self.text)


class Comparison(DB.Model):
    """Comparison between twitter users and a user generated tweet, and prediction/
    probabilities for which user is more likely to have tweeted the tweet"""
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    text = DB.Column(DB.Unicode(300))
    predicted_user = DB.Column(DB.String(15), nullable=False)
    user1_name = DB.Column(DB.String(15), nullable=False)
    user2_name = DB.Column(DB.String(15), nullable=False)
    user1_prob = DB.Column(DB.Float, nullable=False)
    user2_prob = DB.Column(DB.Float, nullable=False)
