import bs4
import re
import requests
import time
import os.path
import random
import time
import logging
import csv
import errno

searchString = 'naked news'
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
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def return_url_content(myURL):
    logger.debug('Entering: return_url_content')
    soup = ''
    logger.info('Parsing URL: {0}'.format(myURL))

    waitTime = random.randrange(3,10,1)
    logger.info('Waiting for {0} seconds before hitting the URL'.format(waitTime))
    time.sleep(waitTime)
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    headers = {'User-Agent': 'Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'}

    res = requests.get(myURL, headers = headers)
    
    try:
        res.raise_for_status()
        #soup = bs4.BeautifulSoup(res.text, 'lxml')
        soup = bs4.BeautifulSoup(res.text, "html.parser")
    except Exception as exc:
        logger.error('There was a problem: %s' % (exc))
	soup = ''

    logger.debug('Exiting: return_url_content')
    return soup

def list_content(soup):
    logger.debug('Entering: list_content')
    result = []
    contents = soup.find_all('a', title = re.compile('view Naked News'))
    for content in contents:
	name = content.get_text()
	href = content.get('href')
        result.append([name,href])
    logger.debug('Exiting: list_content')
    return result

def list_others(soup):
    logger.debug('Entering: list_others')
    result = []
    contents = soup.find_all('a', title = re.compile('View Torrent Info:'))
    for content in contents:
	name = content.get('title').split(':')[-1].strip()
	href = content.get('href')
        result.append([name,href])
    logger.debug('Exiting: list_others')
    return result

def return_magnet(soup):
    logger.debug('Entering: return_magnet')
    mlink = soup.find('a', title = 'Magnet link').get('href')
    logger.debug('Exiting: return_magnet')
    return mlink

def print_list2CSV(contentList, outputFile):
    logger.debug('Entering: print_list2CSV')

    print contentList
    with open(outputFile, 'ab') as fh:
         csvWriter = csv.writer(fh, quoting = csv.QUOTE_ALL)
	 csvWriter.writerows(contentList)

    logger.debug('Exiting: print_list2CSV')

def print_list(contentList, outputFile):
    logger.debug('Entering: print_list')

    if not os.path.isfile(outputFile):
       fh = open(outputFile, 'w')
    else:
       fh = open(outputFile, 'a')

    logger.info('Writing to file: {0}'.format(outputFile))
    for content in contentList:
        #print '{0}'.format(content)
        fh.write(','.join(content)+'\n')

    fh.close()
    logger.debug('Exiting: print_list')

def mkdir_path(path):
    try:
       os.makedirs(path)
    except os.error, e:
       if e.errno != errno.EEXIST:
          raise

def main():
    logger.debug('Entering: main')
    startTime = time.time()
    maxMagnet = 5
    count = 0
    fileExt = '.csv'
    outputDir = 'output'
    mkdir_path(outputDir)

    outputFile = str(int(time.time()))+fileExt
    outputFile = (os.path.join(outputDir, outputFile))

    #searchURL = 'https://extratorrent.cc/search/?search=naked+news&new=1&x=0&y=0'
    baseURL = 'https://extratorrent.cc'
    searchURL = baseURL+'/search/?search='+searchString+'&new=1&x=0&y=0'
    soup = return_url_content(searchURL)
    if soup:
       contentList = list_content(soup)

       for content in contentList:
           partURL = content[1]
           soupm = return_url_content(baseURL+partURL)
           content[1] = baseURL + partURL
	   if soupm:
              mLink = return_magnet(soupm)
	      if mLink:
	         content.append(mLink)
	         count += 1
	      if count > maxMagnet:
	         break
    
       print_list2CSV(contentList, outputFile)

       contentList = list_others(soup)
       for content in contentList:
           partURL = content[1]
           soupm = return_url_content(baseURL+partURL)
	   if soupm:
              mLink = return_magnet(soupm)
	      if mLink:
	         content.append(mLink)

       print_list2CSV(contentList, outputFile)
    else:
       logger.error('No data\n')

    logger.info('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))
    logger.debug('Exiting: main')
main()
