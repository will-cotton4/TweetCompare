"""Retrieves tweets, embeddings, and persist in database."""

from os import getenv
import basilica
import tweepy
from .models import DB, Tweet, User

TWITTER_USERS = ['calebhicks', 'elonmusk', 'rrherr', 'SteveMartinToGo',
                 'austen']

TWITTER_AUTH = tweepy.OAuthHandler(getenv('TWITTER_CONSUMER_KEY'),
                                   getenv('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(getenv('TWITTER_ACCESS_TOKEN'),
                              getenv('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(getenv('BASILICA_KEY'))


def add_or_update_user(username):
    """
    Add or update user and their tweets, else error if not a twitter user
    """
    try:
        twitter_user = TWITTER.get_user(username)
        # TODO: get picture, follower count, etc.
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=username))
        DB.session.add(db_user)
        tweets = twitter_user.timeline(
            count=250, exclude_replies=True, include_rts=False,
            tweet_mode='extended', since_id=db_user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],
                             embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print("Error processing {}: {}".format(username, e))
        raise e
    else:
        DB.session.commit()


def display_user_tweets(username):
    twitter_user_id = User.query.filter(User.name == username).all()[0].id
    tweets = Tweet.query.filter(Tweet.user_id == twitter_user_id)

    return tweets


# TODO
def add_users(users=TWITTER_USERS):
    """
    Add/update list of users.
    """
    for user in users:
        add_or_update_user(user)
