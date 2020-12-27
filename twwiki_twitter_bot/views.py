from django.shortcuts import render
from .models import Wiki_Tweet
from django.utils import timezone
from .wiki_test import mainMethod
from . import wiki_tweets


# Create your views here.


def testView(request):
    testMats = mainMethod()
    return render(request, 'twwiki_twitter_bot/test.html', {'testMats': testMats})


def nada(request):
    return render(request, 'twwiki_twitter_bot/nada.html')

def pullTweets(request):
    wiki_tweets.tweetEvents()
    return render(request, 'twwiki_twitter_bot/nada.html')
    