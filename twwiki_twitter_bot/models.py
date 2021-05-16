from django.conf import settings
from django.db import models
from django.utils import timezone
import datetime
import os

# Create your models here.

class Wiki_Tweet(models.Model):
    text = models.TextField(blank=True, null=True)
    mainMedia = models.TextField(blank=True, null=True)
    originalHTML = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    isDateTweetField = models.BooleanField(default=False)

    @classmethod
    def create(cls):
        tweet = cls()
        return tweet

    def __str__(self):
        if self.text is None:
            return ""
        return self.text
    
    def setMainMedia(self, theFile):
        self.mainMedia = theFile
        self.save()
    
    def setHTML(self, theHTML):
        self.originalHTML = theHTML
        self.save()
    
    def setText(self, theText):
        self.text = theText
        self.save()

    def markAsDateTweet(self):
        self.isDateTweetField = True
        self.save()
    
    def isDateTweet(self):
        return self.isDateTweetField

    def markAsPublished(self):
        self.published_date = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        self.save()

    def clearFile(self):
        try: 
            os.remove(mainMedia)
        except:
            print("removing file failed")
     