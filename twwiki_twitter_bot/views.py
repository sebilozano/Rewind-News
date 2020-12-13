from django.shortcuts import render
from .models import Wiki_Tweet
from django.utils import timezone


# Create your views here.

def tweet_list(request):
    tweets = Wiki_Tweet.objects.filter(created_date__lte=timezone.now()).order_by('created_date')
    return render(request, 'twwiki_twitter_bot/tweet_list.html', {'tweets': tweets})