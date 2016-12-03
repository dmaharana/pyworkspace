#!/usr/bin/python

import requests
from bs4 import BeautifulSoup 
import re
import csv, codecs

def main():
    print 'Entering main'
    headerRow = ['Comment', 'Recommendation', 'Rating']
    dataDic = {}
    #outFile = '11result.csv'
    outFile = 'autoportal.csv'
    counter = 0
    #myurls = ['http://www.mouthshut.com/product-reviews/tata-sky-ltd-tata-reviews-925857022-srch', 'http://www.mouthshut.com/product-reviews/tata-sky-ltd-tata-reviews-925857022-page-2', 'http://www.mouthshut.com/product-reviews/tata-sky-ltd-tata-reviews-925857022-page-3']

    #myurls = ['http://navbharattimes.indiatimes.com/movie-masti/movie-masti/movie-review/articlelist/2325387.cms']
    myurls = ['https://autoportal.com/newcars/renault/kwid/reviews/']

    for counter in range(len(myurls)):
        dataDic = parseWebContent(openURL(myurls[counter]))
        write2csv([], dataDic, outFile)

    print 'Exiting main'

def openURL(myurl):
    print 'Entering openURL'
    res = requests.get(myurl)
    res.raise_for_status()
    print 'Exiting openURL'
    return res.text

def parseWebContent(fileName):
    print 'Entering parseWebContent'
    dataDic = {}
    counter = 0
 
    soup = BeautifulSoup(fileName,'lxml')

    #comments = soup.find_all('p')
    #ratingsAll = soup.find_all('span', itemprop = 'ratingValue')
    comments = soup.find_all('div',itemprop='description')    

    ratingsAll = soup.find_all('span', class_ = 'rating-status')	
    ratingsSite = []
    for rating in ratingsAll:
        rating = rating.get_text().replace(u'\xa0 Read\xa0More\xa0\xbb','')
        ratingsSite.append(rating)

    for counter in range(len(comments)):
        dataDic[counter] = [comments[counter].get_text().replace(u'\xa0 Read\xa0More\xa0\xbb',''), ratingsSite[counter]]
        
	#dataDic[counter] = [comments[counter], ratingsSite[counter]]
    print 'Exiting parseWebContent'
    return dataDic

def write2csv(headerRow, dataDic, outFile):
    print 'Entering write2csv'
    #with open(outFile, 'wb') as csvfile:
    with open(outFile, 'ab') as csvfile:
         spamwriter = csv.writer(csvfile, quoting = csv.QUOTE_ALL)
         if len(headerRow) > 0:
            spamwriter.writerow(headerRow)

         for index in dataDic:
             utf8Data = []
             for col in dataDic[index]:
                 col = col.encode('utf-8')
                 #col = col.replace(u"\x92", u"\u2019")
                 #col = col.replace(u"\xc2", u"\u00C2")
                 #col = col.replace(u"\x92", "'")
                 #col = col.replace(u"\xc2", "")
                 #print 'Data2write: {0}'.format(col)
                 utf8Data.append(col)

             #print 'before writing: {0}'.format(utf8Data)
             spamwriter.writerow(utf8Data)
    csvfile.close()
    print 'Exiting write2csv'
   

main()
