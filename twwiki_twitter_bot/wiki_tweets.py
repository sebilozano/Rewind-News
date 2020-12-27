from django.utils import timezone
from bs4 import BeautifulSoup
from .models import Wiki_Tweet
import wikipedia
import os
import tweepy
import requests
from PIL import Image
from urllib.error import HTTPError
from urllib.request import urlretrieve
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()




def getOnThisDayTweets():

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

        wiki_tweet = Wiki_Tweet()
        wiki_tweet.setText(constructed_tweet)
        wiki_tweet.setHTML(todayString)
        wiki_tweets.append(wiki_tweet)

    ## pull the list of events for that day
    otd_event_list_html = mp_otd.ul
    for bullet in otd_event_list_html.find_all("li"):
        wiki_tweet = Wiki_Tweet()
        wiki_tweet.setHTML = bullet

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

        wiki_tweets.append(wiki_tweet)

    return wiki_tweets

def tweetEvents():
    wiki_tweet_list = getOnThisDayTweets()
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)

    for wiki_tweet in wiki_tweet_list:
        
        if wiki_tweet.mainMedia != None:
            media_obj = api.media_upload(wiki_tweet.mainMedia)
            api.update_status(status=wiki_tweet.text, media_ids = [media_obj.media_id])
        else:
            api.update_status(status=wiki_tweet.text)

def getRequestLinkFromBoldedContent(content, domain):
    bolded_part = content.find("b")
    page_link = domain + bolded_part.find("a")["href"]
    return page_link


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
        first_img_link = content.find("a", {"class": "image"})['href']
        img_path = first_img_link
        
    if (img_path != ''):
        # create url
        img_path = 'https://en.wikipedia.org' + (img_path)
        return img_path
    
    
    return img_path
    
