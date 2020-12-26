from django.shortcuts import render
from .models import Wiki_Tweet
from django.utils import timezone
from .wiki_test import mainMethod


# Create your views here.


def testView(request):
    testMats = mainMethod()
    return render(request, 'twwiki_twitter_bot/test.html', {'testMats': testMats})
