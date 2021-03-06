from django.utils import timezone
from bs4 import BeautifulSoup
from .models import Wiki_Tweet
import wikipedia
import os
import tweepy
import glob
import requests
from PIL import Image
import datetime
from urllib.error import HTTPError
from urllib.request import urlretrieve
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()


def tweetNextEventScheduled():
    timestamp = datetime.datetime.now(datetime.timezone.utc).time()
    start = datetime.time(13)
    end = datetime.time(23)
    print(timestamp)
    print (start <= timestamp <= end)
    if (start <= timestamp <= end):
        tweetNextEvent()
    return

def tweetNextEvent():

    # check that there are tweets created today 
    todayTweets = Wiki_Tweet.objects.filter(created_date__gte=timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()).replace(hour=0, minute=0, second=0), created_date__lte=timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()).replace(hour=23, minute=59, second=59)).order_by('created_date')
    print("hey_tweetNextEvent")

    if len(todayTweets) == 0:
        getOnThisDayTweets()
        print("hey_todayTweetsLenZero")
        #tweetNextEvent()
        return

    print("KEPT GOING")
    nonPublishedTodayTweets = todayTweets.filter(published_date__isnull=True).order_by('created_date')
    if len(nonPublishedTodayTweets) > 0:
        if nonPublishedTodayTweets[0].isDateTweet():
            publishWikiTweet(nonPublishedTodayTweets[0])
            publishWikiTweet(nonPublishedTodayTweets[1])
        else:
            publishWikiTweet(nonPublishedTodayTweets[0])
    else: 
        cleanMediaFolder()
    
def publishWikiTweet(wiki_tweet):
    api = generateTwitterAPI()

    if wiki_tweet.mainMedia != None:
        try:
            print(wiki_tweet.mainMedia)
            media_obj = api.media_upload(wiki_tweet.mainMedia)
            tweetStatus = api.update_status(status=wiki_tweet.text, media_ids = [media_obj.media_id])
            publishWikiTweetLinks(wiki_tweet.originalHTML, tweetStatus, api)
        except tweepy.TweepError as err:
            print(err)
            try:
                tweetStatus = api.update_status(status=wiki_tweet.text)
                publishWikiTweetLinks(wiki_tweet.originalHTML, tweetStatus, api)
            except tweepy.TweepError as err:
                print(err)
        except FileNotFoundError as err:
            try:
                tweetStatus = api.update_status(status=wiki_tweet.text)
                publishWikiTweetLinks(wiki_tweet.originalHTML, tweetStatus, api)
            except tweepy.TweepError as err:
                print(err)
    else:
        try:
            tweetStatus = api.update_status(status=wiki_tweet.text)
            publishWikiTweetLinks(wiki_tweet.originalHTML, tweetStatus, api)
        except tweepy.TweepError as err:
            print(err)
    
    wiki_tweet.markAsPublished()


def cleanMediaFolder():
    files = glob.glob(settings.MEDIA_ROOT + "/*")
    for f in files:
        os.remove(f)

def getOnThisDayTweets():
    print("get those tweets!")
    soup = BeautifulSoup(wikipedia.WikipediaPage(pageid = '15580374').html(), features="html.parser")
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


        
        wiki_tweet = Wiki_Tweet.create()
        print("WIKI_TWEET STEP 0")
        wiki_tweet.setText(constructed_tweet)
        print(wiki_tweet)
        print("today string")
        print(todayString)
        wiki_tweet.setHTML(str(originalHeader))
        wiki_tweet.markAsDateTweet()
        wiki_tweets.append(wiki_tweet)
        print("WIKI_TWEET STEP 1")
        print(wiki_tweets)

    ## pull the list of events for that day
    otd_event_list_html = mp_otd.ul
    for bullet in otd_event_list_html.find_all("li"):
        wiki_tweet = Wiki_Tweet.create()
        print("WIKI_TWEET STEP 2")
        print(wiki_tweet)
        print("COMING UP")
        print(bullet)
        

        #if it says (pictured) or (depicted) in italics, then pull from that
        if isPicturedTweet(bullet):
            tweet_img_link = getTweetImageLinkforPicturedImageFromWikiMainPage(mp_otd, "https://en.wikipedia.org")
        else: 
            #get bolded link
            page_link = getRequestLinkFromBoldedContent(bullet, "https://en.wikipedia.org")
            tweet_img_link = getTweetImageLink(page_link)

        if (tweet_img_link != ''):
            img_file = downloadImage(tweet_img_link)
            wiki_tweet.setMainMedia(img_file)
        
        cleaned_bullet = "#OnThisDay in " + bullet.text
        #handle long tweets
        cleaned_bullet_trunc = (cleaned_bullet[:277] + '...') if len(cleaned_bullet) > 280 else cleaned_bullet
        wiki_tweet.setText(cleaned_bullet_trunc)
        print("WIKI_TWEET STEP 4")
        print(wiki_tweet)
        wiki_tweet.setHTML(str(bullet))
        print(wiki_tweet)

        wiki_tweets.append(wiki_tweet)

    return wiki_tweets

def generateTwitterAPI():
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)
    return api


#DEPRECATED
def tweetEvents():
    wiki_tweet_list = getOnThisDayTweets()
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)

    for wiki_tweet in wiki_tweet_list:
        if wiki_tweet.mainMedia != None:
            try:
                media_obj = api.media_upload(wiki_tweet.mainMedia)
                api.update_status(status=wiki_tweet.text, media_ids = [media_obj.media_id])
            except tweepy.TweepError as err:
                print(err)
                try:
                    api.update_status(status=wiki_tweet.text)
                except tweepy.TweepError as err:
                    print(err)
                    continue
        else:
            try:
                api.update_status(status=wiki_tweet.text)
            except tweepy.TweepError as err:
                print(err)
                continue

    #clean media folder
    cleanMediaFolder()


def getRequestLinkFromBoldedContent(content, domain):
    bolded_part = content.find("b")
    page_link = domain + bolded_part.find("a")["href"]
    return page_link

def getTweetImageLinkforPicturedImageFromWikiMainPage(content, domain):
    page_link = domain + content.find("a", {"class": "image"})["href"]
    return page_link

def isPicturedTweet(content):
    italic_parts = content.find_all("i") 
    for i in italic_parts:
        i = i.text.lower()
        if ("pictured" in i) or ("depicted" in i):
            return True
    return False

def optimizeImage(fileName):
    counter = 500
    while ((os.path.getsize(fileName) / 1000 > 4880)):
        if (counter == 200):
            return None
        img = Image.open(fileName)
        maxsize = (counter,counter)
        img.thumbnail(maxsize)
        img.save(fileName, optimizeImage=True)
        counter = counter - 100
    return fileName

def downloadImage(img_path):
    soup = BeautifulSoup(requests.get(img_path).content, features="html.parser")
    img_link = "https:" + soup.find("div", {"class": "fullImageLink"}).find("a")["href"]
    path_split = img_path.split("/")
    img_name = path_split[len(path_split) - 1].replace("File:", '')
    save_path = settings.MEDIA_ROOT + "/" + img_name
    try:
        file, header = urlretrieve(img_link, save_path)
        file = optimizeImage(file)
        return file
    except FileNotFoundError as err:
        print(err)   # something wrong with local path
        return ''
    except HTTPError as err:
        print(err)  # something wrong with url
        return ''
    except:
        print("other exception downloading image")
        return ''

def getTweetImageLink(requestLink):
    print(requestLink)
    soup = BeautifulSoup(requests.get(requestLink).content, features="html.parser")
    infobox = soup.find("table", {"class": "infobox"})

    if infobox == None: # sometimes there isn't an infobox (i.e https://en.wikipedia.org/wiki/1990_Slovenian_independence_referendum)
        infobox = soup.find("table", {"class": "vcard"})
    
    img_arr = []

    img_path = ''
    index = 0

    if infobox != None: 
        for i, tr in enumerate(infobox.find_all("tr")):
            images_in_row = tr.find_all("a", {"class": "image"})
            numImagesInRow = len(images_in_row)

            row_img_list = []
            for j, img in enumerate(images_in_row):
                row_img_list.append(img['href'])

            if (len(row_img_list) == 1):
                img_path = row_img_list[0]
                break
            elif (len(row_img_list) > 1):
                img_arr.insert(index, row_img_list)
                index += 1


    # if no single pic, pick the first image in the infobox
    if (img_path == '' and len(img_arr) > 0):
        img_path = img_arr[0][0]

    # if no pics, pick the first pic on page
    elif (img_path == ''):

        content = soup.find("div", {"class": "mw-parser-output"})

        #remove junk for if eventually I want to pick randomly, see bottom of Plymouth Colony page
        for div in content.find_all("div", class_='navbox'):
            div.decompose()

        #print(content.find("a", {"class": "image"}))
        first_img = content.find("a", {"class": "image"})
        
        if first_img != None:
            first_img_link = first_img['href']
            img_path = first_img_link
        else: 
            return ''
        
    if (img_path != ''):
        # create url
        img_path = 'https://en.wikipedia.org' + (img_path)
        return img_path
    
    
    return img_path
    
def publishWikiTweetLinks(content, tweetStatus, api):
    soup = BeautifulSoup(content, features="html.parser")
    for tag in soup.find_all("b"):
        link = tag.find("a")
        if link != None:
            link = 'https://en.wikipedia.org' + str(link["href"])
            #NOTE TODO: change this to @OnThisDayTestA1 when testing
            linkTweet = '@OnThisDayIH ' + str(link)
            api.update_status(status=linkTweet, in_reply_to_status_id=tweetStatus.id_str)
    return