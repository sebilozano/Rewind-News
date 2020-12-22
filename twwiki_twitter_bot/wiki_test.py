from bs4 import BeautifulSoup
import wikipedia
import requests
import wiki_tweets
import os
import tweepy
import requests
from dotenv import load_dotenv
load_dotenv()



# for each <tr> in infobox
#     put images in an array
#     count images
#     if count(img) = 1, then stop
#     else continue
# if len(img_arr) > 0, then get img_arr[1]
# else getAllImages 

soup = BeautifulSoup(requests.get("https://en.wikipedia.org/wiki/Plymouth_Colony").content)
infobox = soup.find("table", {"class": "infobox"})

#print(infobox.find_all("tr"))

img_arr = []

print(len(img_arr))

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
    img_link = img_arr[0][0]
elif (img_path == ''):
    img_path = ''
    # to do: no img in infobox
    # content = soup.find("div", {"class": "mw-parser-output"})

    # #remove junk
    # for div in content.find_all(("div", {"class": "navbox"})):
    #     div.decompose()
    
    # img_link_list = content.find_all("a", {"class": "image"})
    # print(len(img_link_list))

if (img_path != ''):
    # create url
    img_path = 'https://en.wikipedia.org' + (img_path)
    print(img_path)
    









    





