from bs4 import BeautifulSoup
import wikipedia
import requests
import wiki_tweets
import os
import tweepy
from dotenv import load_dotenv
load_dotenv()

def tweetEvents():
    wiki_tweet_list = wiki_tweets.getOnThisDayTweets()
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)

    for tweet in wiki_tweet_list:
        api.update_status(tweet)


tweetEvents()
