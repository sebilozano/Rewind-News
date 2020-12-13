from django.shortcuts import render

# Create your views here.

def tweet_list(request):
    return render(request, 'twwiki_twitter_bot/tweet_list.html', {})