from bs4 import BeautifulSoup
import wikipedia
import requests
import wiki_tweets
import os
import tweepy
from dotenv import load_dotenv
load_dotenv()

soup = BeautifulSoup(wikipedia.WikipediaPage(pageid = '15580374').html())
mp_otd = soup.find("div", {"id": "mp-otd"})
wiki_tweets = []
## pull whether this is a named day
originalHeader = mp_otd.find("p")
todayString = originalHeader.find("b").text
todayStringToMatch = todayString + ": "
almost_cleaned_header = mp_otd.find("p").text.replace(todayStringToMatch, '')
cleaned_header = almost_cleaned_header.replace('\n', '').strip()
if (almost_cleaned_header != originalHeader.text):
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
    wiki_tweets.append(cleaned_bullet_trunc)
    print(cleaned_bullet_trunc)
    print('--------')

print(wiki_tweets[0])