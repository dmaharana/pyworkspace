import bs4
import re
import requests
import time
import os.path
import random
import time
import logging

#soup.find_all('td', class_ = 'sn')
#soup.find_all('td', class_ = 'sy')
#soup.find_all('a', style = re.compile('color'))[2].get_text()

#soup.find_all('a', title = re.compile('view Naked News'))
#soup1.find('a', title = 'Magnet link').get('href')

#soup.find_all('a', title = re.compile('View Torrent Info:'))[0].get('href')
#soup.find_all('a', title = re.compile('View Torrent Info:'))[0].get('title').split(':')[-1].strip()

mylogFile = 'nn.log'
# create logger
logger = logging.getLogger('nn')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(mylogFile)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def return_url_content(myURL):
    logger.info('Entering: return_url_content')
    soup = ''
    logger.info('Parsing URL: {0}'.format(myURL))

    waitTime = random.randrange(3,10,1)
    logger.info('Waiting for {0} seconds before hitting the URL'.format(waitTime))
    time.sleep(waitTime)

    res = requests.get(myURL)
    
    try:
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    except Exception as exc:
        logger.error('There was a problem: %s' % (exc))
	soup = ''

    logger.info('Exiting: return_url_content')
    return soup

def list_content(soup):
    logger.info('Entering: list_content')
    result = []
    contents = soup.find_all('a', title = re.compile('view Naked News'))
    for content in contents:
	name = content.get_text()
	href = content.get('href')
        result.append([name,href])
    logger.info('Exiting: list_content')
    return result

def list_others(soup):
    logger.info('Entering: list_others')
    result = []
    contents = soup.find_all('a', title = re.compile('View Torrent Info:'))
    for content in contents:
	name = content.get('title').split(':')[-1].strip()
	href = content.get('href')
        result.append([name,href])
    logger.info('Exiting: list_others')
    return result

def return_magnet(soup):
    logger.info('Entering: return_magnet')
    mlink = soup.find('a', title = 'Magnet link').get('href')
    logger.info('Exiting: return_magnet')
    return mlink

def print_list(contentList, outputFile):
    logger.info('Entering: print_list')

    if not os.path.isfile(outputFile):
       fh = open(outputFile, 'w')
    else:
       fh = open(outputFile, 'a')

    logger.info('Writing to file: {0}'.format(outputFile))
    for content in contentList:
        #print '{0}'.format(content)
        fh.write(','.join(content)+'\n')

    fh.close()
    logger.info('Exiting: print_list')

def main():
    logger.info('Entering: main')
    startTime = time.time()
    maxMagnet = 5
    count = 0
    fileExt = '.csv'
    outputFile = str(int(time.time()))+fileExt

    searchURL = 'https://extratorrent.cc/search/?search=naked+news&new=1&x=0&y=0'
    baseURL = 'https://extratorrent.cc'
    soup = return_url_content(searchURL)
    if soup:
       contentList = list_content(soup)

       for content in contentList:
           partURL = content[1]
           soupm = return_url_content(baseURL+partURL)
	   if soupm:
              mLink = return_magnet(soupm)
	      if mLink:
	         content.append(mLink)
	         count += 1
	      if count > maxMagnet:
	         break
    
       print_list(contentList, outputFile)

       contentList = list_others(soup)
       for content in contentList:
           partURL = content[1]
           soupm = return_url_content(baseURL+partURL)
	   if soupm:
              mLink = return_magnet(soupm)
	      if mLink:
	         content.append(mLink)

       print_list(contentList, outputFile)
    else:
       logger.error('No data\n')

    logger.info('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))
    logger.info('Exiting: main')
main()
