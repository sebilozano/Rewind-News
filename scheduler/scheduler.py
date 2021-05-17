from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
import twwiki_twitter_bot.wiki_tweets
import datetime
import time
##from twwiki_twitter_bot.wiki_tweets import tweetNextEvent
import sys


def tweetNextEvent():
    print("hey_tweetNextEvent_SCHEDULER")
    timestamp = datetime.datetime.now(datetime.timezone.utc).time()
    start = datetime.time(13)
    end = datetime.time(23)
    print(timestamp)
    print (start <= timestamp <= end)
    twwiki_twitter_bot.wiki_tweets.tweetNextEvent()

def start():
    
    scheduler = BackgroundScheduler()
    
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    ##run every 80 minutes from 8am EST to 6pm EST (1pm-11pm UTC)
    #trigger = OrTrigger([
    #     CronTrigger(hour='13-23', minute='*/80' timezone='UTC')
    #])

    trigger = OrTrigger([
        CronTrigger(minute='*/1', timezone='UTC')
    ])
    scheduler.add_job(
        tweetNextEvent, 
        trigger=trigger,
        name='tweetNextEvent', 
        jobstore='default',
        max_instances=1,
        replace_existing=True)
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout, flush=True)

    