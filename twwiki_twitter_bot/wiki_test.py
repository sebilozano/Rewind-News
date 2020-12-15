from bs4 import BeautifulSoup
import wikipedia
import requests
import wiki_tweets
import os
import tweepy
from dotenv import load_dotenv
load_dotenv()

wiki_tweets.tweetEvents()
