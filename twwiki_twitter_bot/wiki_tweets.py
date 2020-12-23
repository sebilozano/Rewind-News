from django.utils import timezone
from bs4 import BeautifulSoup
import wikipedia
import os
import tweepy
import requests
from django.conf import settings
from urllib.error import HTTPError
from urllib.request import urlretrieve
from dotenv import load_dotenv
load_dotenv()




def getOnThisDayTweets():

    soup = BeautifulSoup(wikipedia.WikipediaPage(pageid = '15580374').html())
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

        wiki_tweets.append(constructed_tweet)

    ## pull the list of events for that day
    otd_event_list_html = mp_otd.ul
    for bullet in otd_event_list_html.find_all("li"):
        #get bolded link
        page_link = getRequestLinkFromBoldedContent(bullet, "https://en.wikipedia.org")
        tweet_img_link = getTweetImageLink(page_link)
        if (tweet_img_link != ''):
            print(tweet_img_link)
            local_img_path = downloadImage(tweet_img_link)
        

        cleaned_bullet = "#OnThisDay in " + bullet.text.replace(' (pictured)', '') #remove (pictured) reference
        cleaned_bullet_trunc = (cleaned_bullet[:277] + '...') if len(cleaned_bullet) > 280 else cleaned_bullet

        wiki_tweets.append(cleaned_bullet_trunc)

    return wiki_tweets

def tweetEvents():
    wiki_tweet_list = getOnThisDayTweets()
    auth = tweepy.OAuthHandler(os.getenv("twitter_consumer_key"), os.getenv("twitter_consumer_secret"))
    auth.set_access_token(os.getenv("bot_access_token"), os.getenv("bot_access_token_secret"))
    api = tweepy.API(auth)

    for tweet in wiki_tweet_list:
        # here is where I have to add the logic TODO
        api.update_status(tweet)

def getRequestLinkFromBoldedContent(content, domain):
    bolded_part = content.find("b")
    page_link = domain + bolded_part.find("a")["href"]
    return page_link
    print("TODO")


def downloadImage(img_path):
    print("TODO")
    soup = BeautifulSoup(requests.get(img_path).content)
    img_link = "https:" + soup.find("div", {"class": "fullImageLink"}).find("a")["href"]
    path_split = img_path.split("/")
    img_name = path_split[len(path_split) - 1].replace("File:", '')
    #print(settings.MEDIA_ROOT + "/" + img_name)
    
    try:
        #file, header = urlretrieve(img_link)
        print("hi") 
        #print(header)
    except FileNotFoundError as err:
        print(err)   # something wrong with local path
        return ''
    except HTTPError as err:
        print(err)  # something wrong with url
        return ''
    

    print("return location of img on system")


def getTweetImageLink(requestLink):
    soup = BeautifulSoup(requests.get(requestLink).content)
    infobox = soup.find("table", {"class": "infobox"})

    if infobox == None: # sometimes there isn't an infobox (i.e https://en.wikipedia.org/wiki/1990_Slovenian_independence_referendum)
        infobox = soup.find("table", {"class": "vcard"})

    if infobox == None: # error handling if there isn't either
        return ''
    
    img_arr = []

    img_path = ''
    index = 0

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



    if (img_path == '' and len(img_arr) > 0):
        img_path = img_arr[0][0]
    elif (img_path == ''):
        img_path = ''
        # TODO: no img in infobox
        # content = soup.find("div", {"class": "mw-parser-output"})

        # #remove junk
        # for div in content.find_all(("div", {"class": "navbox"})):
        #     div.decompose()

        # img_link_list = content.find_all("a", {"class": "image"})
        
    if (img_path != ''):
        # create url
        img_path = 'https://en.wikipedia.org' + (img_path)
        return img_path
    
    return img_path
    