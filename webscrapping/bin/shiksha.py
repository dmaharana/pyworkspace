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
    myURL = 'http://www.shiksha.com/engineering-colleges-reviews-cr'
    dataDic = {}
    outFile = 'shiksha.csv'
    
    print 'Read URL: {0}'.format(myURL)
    soup = BeautifulSoup(openURL(myURL), 'lxml')
    

    while 1:
       dataDic = parseWebContent(soup)
       if any (dataDic):
          write2csv(dataDic, outFile)
       #break

       nextURL = soup.find_all('a', href = re.compile('http://www.shiksha.com/engineering-colleges-reviews-cr'))[-1].get('href')
       if nextURL:
          print 'Waiting before reading next URL...'
          time.sleep(3)
          print 'Read URL: {0}'.format(nextURL)
          soup = BeautifulSoup(openURL(nextURL), 'lxml')
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
    comments = []

    commentsAll = soup.find_all('div',class_ = "rv_desc")
 
    for index in range(len(commentsAll)):
        if index % 2 == 0:
           comments.append(commentsAll[index].text.strip())
        else:
           comments[-1] = comments[-1] + commentsAll[index].text.strip()
    
    ratings = soup.find_all('div', class_ = 'rv_ratng')

    for counter in range(len(comments)):
        dataDic[counter] = [comments[counter], ratings[counter].get_text().strip().split('\t')[-1]]
        

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
