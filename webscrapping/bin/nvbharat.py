#!/usr/bin/python

import requests
from bs4 import BeautifulSoup 
import re
import csv, codecs
import time

# read the base url
# extract the site url
# extract the reviews and corresponding rating on the page
# save the extract to a csv
# check if there is next url
# go to extract site url by appending the next url to the site url
# else exit

def main():
    myURL = 'http://navbharattimes.indiatimes.com/movie-masti/movie-masti/movie-review/articlelist/2325387.cms'
    dataDic = {}
    outFile = 'navbharat2.csv'
    
    print 'Read URL: {0}'.format(myURL)
    soup = BeautifulSoup(openURL(myURL), 'html')
    siteURL = soup.find('meta', property = 'og:site_name').get('content')

    while 1:
       dataDic = parseWebContent(soup)
       if any (dataDic):
          write2csv(dataDic, outFile)

       nextURL = soup.find('a', class_ = 'spannext').get('href')
       if nextURL:
          print 'Waiting before reading next URL...'
          time.sleep(3)

          myURL = siteURL +  nextURL
          print 'Read URL: {0}'.format(myURL)
          soup = BeautifulSoup(openURL(myURL), 'html')cd Dict
       else:
          break
    
def openURL(myurl):
    print 'Entering openURL'
    res = requests.get(myurl)
    res.raise_for_status()
    print 'raise {0}'.format(res.raise_for_status())
    print 'Exiting openURL'
    return res.text

def parseWebContent(soup):
    print 'Entering parseWebContent'
    dataDic = {}
    counter = 0

    comments = soup.find_all('p')
    ratingsAll = soup.find_all('span', itemprop = 'ratingValue')
    ratingsSite = []
    for rating in ratingsAll:
        rating = rating.get_text()
        if '/' not in rating:
          ratingsSite.append(rating)

    for counter in range(len(comments)):
        dataDic[counter] = [comments[counter].text.strip(), ratingsSite[counter]]
        

    print 'Exiting parseWebContent'
    return dataDic

def write2csv(dataDic, outFile):
    print 'Entering write2csv'
    with open(outFile, 'ab') as csvfile:
         spamwriter = csv.writer(csvfile, quoting = csv.QUOTE_ALL)

         for index in dataDic:
             utf8Data = []
             for col in dataDic[index]:
                 col = col.encode('utf-8')
                 utf8Data.append(col)

             #print 'before writing: {0}'.format(utf8Data)
             spamwriter.writerow(utf8Data)

    csvfile.close()
    print 'Exiting write2csv'

main()
