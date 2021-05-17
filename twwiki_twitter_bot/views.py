from django.shortcuts import render
from .models import Wiki_Tweet
from django.utils import timezone
from .wiki_test import mainMethod
from . import wiki_tweets


# Create your views here.


def testView(request):
    wiki_tweets.tweetNextEvent()
    return render(request, 'twwiki_twitter_bot/test.html')


def nada(request):
    return render(request, 'twwiki_twitter_bot/nada.html')

def pullTweets(request):
    wiki_tweets.tweetNextEventScheduled()
    return render(request, 'twwiki_twitter_bot/nada.html')
    