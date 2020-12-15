from django.utils import timezone
from bs4 import BeautifulSoup
import wikipedia
import os
import tweepy
from dotenv import load_dotenv
load_dotenv()




def getOnThisDayTweets():

    soup = BeautifulSoup(wikipedia.WikipediaPage(pageid = '15580374').html())
    mp_otd = soup.find("div", {"id": "mp-otd"})

    wiki_tweets = []

    ## pull whether this is a named day
    originalHeader = mp_otd.find("p")
    todayString = originalHeader.find("b").text
    todayStringToMatch = todayString + ": "
    cleaned_header = mp_otd.find("p").text.replace(todayStringToMatch, '')
    cleaned_header = cleaned_header.replace('\n', '')
    if (cleaned_header != originalHeader):
        constructed_tweet = "Today is also known as " 
        if len(cleaned_header.split("; ")) > 1:
            for i, dayName in enumerate(cleaned_header.split("; ")):
                if i > 0:
                    constructed_tweet = constructed_tweet + " and " + dayName 
                else: constructed_tweet = constructed_tweet + dayName
        else:
            constructed_tweet = constructed_tweet + cleaned_header

        wiki_tweets.append(constructed_tweet)

    ## pull the list of events for that day
    otd_event_list_html = mp_otd.ul
    for bullet in otd_event_list_html.find_all("li"):
        cleaned_bullet = "#OnThisDay in " + bullet.text.replace(' (pictured)', '') #remove (pictured) reference
        cleaned_bullet_trunc = (cleaned_bullet[:277] + '...') if len(cleaned_bullet) > 280 else cleaned_bullet

        wiki_tweets.append(cleaned_bullet)

    return wiki_tweets

def tweetEvents():
    wiki_tweet_list = getOnThisDayTweets()
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)

    for tweet in wiki_tweet_list:
        api.update_status(tweet)