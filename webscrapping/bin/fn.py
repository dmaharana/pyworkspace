import bs4
import re
import requests
import time
import random
import time
import logging
import csv
import codecs

'''
>>> soup.findAll('h3', class_ = 'r')[0].find('a').get_text()
u'10 reasons to buy Apple stock now - MarketWatch'

>>> soup.findAll('h3', class_ = 'r')[0].find('a').get('href')
'http://www.marketwatch.com/story/10-reasons-to-buy-apple-stock-now-2013-12-11'

>>> soup.findAll('div', {'class':'s'})[0].find('cite').get_text()
u"www.marketwatch.com \u203a ... \u203a Stocks \u203a Jeff Reeves's Strength in Numbers"

>>> d1 = soup.findAll('div', {'class':'s'})[0].find('span', {'class':'f'}).get_text()
>>> d1.replace(' - ','')
u'Dec 11, 2013'

>>> t1 = soup.findAll('div', {'class':'s'})[0].find('span', {'class':'st'}).get_text()
u"Dec 11, 2013 - At long last, Apple Inc. is finally in the green year-to-date in 2013. And while the stock has still woefully underperformed the S&P 500, it's undeniable that the tech\xa0..."

>>> t1.replace(d1, '')
u"At long last, Apple Inc. is finally in the green year-to-date in 2013. And while the stock has still woefully underperformed the S&P 500, it's undeniable that the tech\xa0..."


>>> soup.find('a', {'id':'pnnext'}).get('href')
'/search?q=apple+stock&client=ubuntu&hs=Cag&biw=960&bih=906&tbs=cdr:1,cd_min:01/12/2013,cd_max:31/12/2013&ei=jK4_WOfEFojUvgSz26-QAg&start=10&sa=N'
'''

searchURL = 'https://www.google.co.in/search?q=infosys stock news&client=ubuntu&channel=fs&biw=1095&bih=915&noj=1&tbs=cdr:1,cd_min:01/12/2013,cd_max:31/12/2014&ei=ZexAWJLdJcjwvgTN75nYBA&start=0&sa=N'
#searchURL = 'https://www.google.co.in/search?q=apple+inc&client=ubuntu&channel=fs&biw=1095&bih=915&noj=1&tbs=cdr:1,cd_min:01/12/2013,cd_max:31/12/2013&ei=ZexAWJLdJcjwvgTN75nYBA&start=0&sa=N'
#searchURL = 'https://www.google.co.in/search?q=apple+stock&client=ubuntu&hs=nUY&channel=fs&source=lnt&tbs=cdr%3A1%2Ccd_min%3A01%2F12%2F2013%2Ccd_max%3A31%2F12%2F2013&tbm=#channel=fs&tbs=cdr:1%2Ccd_min:01%2F12%2F2013%2Ccd_max:31%2F12%2F2013&q=apple+stock'

baseURL = 'https://www.google.co.in/'

mylogFile = 'gn.log'
# create logger
logger = logging.getLogger('gn')
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


def get_url_content(myURL):
    logger.info('Entering: get_url_content')
    soup = ''
    logger.info('Parsing URL: {0}'.format(myURL))

    waitTime = random.randrange(3,10,1)
    logger.info('Waiting for {0} seconds before hitting the URL'.format(waitTime))
    time.sleep(waitTime)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = requests.get(myURL, headers = headers)

    try:
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    except Exception as exc:
        logger.error('There was a problem: %s' % (exc))
	soup = ''

    logger.info('Exiting: get_url_content')
    return soup

def scrap_page_content(soup):
    logger.info('Entering: scrap_page_content')
    global searchURL

    result = []

    try:
       headerContents = soup.findAll('h3', class_ = 'r')
    except Exception as exc:
       logger.error('Header contents not found: %s' % (exc))
       headerContents = ''
       return result

    searchText = searchURL.split('q=')[1].split('&')[0]
    searchText = searchText.encode('utf-8')

    startDateText = searchURL.split('cd_min')[-1].split(':')[-2]
    indexOfLastPercentage = startDateText.rfind('%')
    startDateText = startDateText[:indexOfLastPercentage].replace('%2F', '/')

    if not startDateText[-1].isdigit():
       startDateText = startDateText.split(',')[0]

    endDateText = searchURL.split('cd_max')[-1].split(':')[-1].split('&')[0].replace('%2F', '/')

    try:
       currentPageNum = soup.find('td', {'class':'cur'}).get_text()
    except Exception as exc:
       logger.error('Page number not found: %s' % (exc))
       currentPageNum = ''

    for headerContent in headerContents:
	try:
           headerText = headerContent.find('a').get_text()
           headerText = headerText.encode('utf-8')
           headerURL = headerContent.find('a').get('href')
	   result.append([searchText, startDateText, endDateText, headerText, headerURL])
        except Exception as exc:
           logger.error('Header Text not found: %s' % (exc))
           logger.info('Exception content: %s' % (headerContent))
           headerText = ''

    try:
       bodyContents = soup.findAll('div', {'class':'s'})

       for index in range(len(bodyContents)):
           bodyContent = bodyContents[index]
	   #print bodyContent

	   snipetText = ''
	   dateText = ''
	   contentText = ''

	   try:
              snipetText = bodyContent.find('cite').get_text()
              snipetText = snipetText.encode('utf-8')
           except Exception as exc:
              logger.error('Next page not found: %s' % (exc))
              logger.info('Exception content: %s' % (bodyContent))
	      snipetText = ''
	

	   try:
	      dateTemp = bodyContent.find('span', {'class':'f'}).get_text()
	      dateText = dateTemp.replace(' - ', '')
	      dateText = dateText.encode('utf-8')
           except Exception as exc:
              logger.warn('Date not found: %s' % (exc))
              logger.info('Exception content: %s' % (bodyContent))
              logger.info('Trying alternate approach to get Date.')

	      try:
	         dateTemp = bodyContent.find('div', {'class':'f slp'}).get_text()
	         dateText = dateTemp.split(' - ')[0]
	         dateText = dateText.encode('utf-8')
              except Exception as exc:
                 logger.error('Date not found: %s' % (exc))
	         dateText = ''

	   try:
	      contentTemp = bodyContent.find('span', {'class':'st'}).get_text()
	      contentText = contentTemp.replace(dateTemp, '')
	      contentText = contentText.encode('utf-8')
           except Exception as exc:
              logger.error('Content not found: %s' % (exc))
              logger.info('Exception content: %s' % (bodyContent))
	      contentText = ''

	   result[index].extend([dateText, contentText, snipetText, currentPageNum,  searchURL])

    except Exception as exc:
           logger.error('Content body not found: %s' % (exc))
           logger.info('Exception content: %s' % (headerContent))

    logger.info('Exiting: scrap_page_content')
    return result

def get_next_page_url(soup):
    logger.info('Entering: get_next_page_url')

    nextPageLink = ''

    try:
        nextPageLink = soup.find('a', {'id':'pnnext'}).get('href')
    except Exception as exc:
        logger.error('Next page not found: %s' % (exc))
	nextPageLink = ''

    logger.info('Exiting: get_next_page_url')
    return nextPageLink

def write_to_csv(contentList, outputFile):
    logger.info('Entering: write_to_csv')

    logger.info('Writing to file: {0}'.format(outputFile))
    #print contentList

    with open(outputFile, 'ab') as fh:
         csvWriter = csv.writer(fh, delimiter = ',', quoting = csv.QUOTE_ALL)
	 csvWriter.writerows(contentList)

    logger.info('Exiting: write_to_csv')

def main():
    logger.info('Entering: main')

    global searchURL
    csvHeader = ['SEARCH_TEXT', 
                 'START_DATE', 
		 'END_DATE', 
		 'CONTENT_HEADLINE', 
		 'CONTENT_URL', 
		 'PUBLISH_DATE', 
		 'SNIPPET_TEXT',    
		 'CONTENT_HEADER_SNIPPET', 
		 'PAGE_NUMBER', 
		 'PAGE_URL']
 
    startTime = time.time()
    maxMagnet = 5
    count = 0
    fileExt = '.csv'
    outputFile = 'gweb_' + str(int(time.time()))+fileExt
    writeHeader = True

    while True:
          soup = get_url_content(searchURL)
          if soup:
             contentList = scrap_page_content(soup)
	  if contentList:
	     if writeHeader:
	        writeHeader = False
		write_to_csv([csvHeader], outputFile)
	     write_to_csv(contentList, outputFile)

	  nextPage = get_next_page_url(soup)

	  if nextPage:
	     searchURL = baseURL + nextPage
	  else:
	     break

    logger.info('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))
    logger.info('Exiting: main')
main()
