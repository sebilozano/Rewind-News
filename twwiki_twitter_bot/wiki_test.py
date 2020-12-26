from . import wiki_tweets
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()

''' #settings.configure()
import os
import django
import sys
print(sys.path)
django.setup()
#print(settings.STATIC_URL)
#print(settings)
 '''

def mainMethod():
    #return wiki_tweets.getOnThisDayTweets
    return wiki_tweets.tweetEvents()
    #return settings

#wiki_tweets.getOnThisDayTweets()