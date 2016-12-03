import re
import re
import request
import codecs
import logging
searchURL = 'https://www.google.co.in/search?q=infosys stock news&client=ubuntu&channel=fs&biw=1095&bih=915&noj=1&tbs=cdr:1,cd_min:01/12/2013,cd_max:31/12/2014&ei=ZexAWJLdJcjwvgTN75nYBA&start=0&sa=N'
baseURL='https://www.google.co.in/'

def main():
    global searchURL
    
    csvHeader = ['search_text','start_date','end_date','content_headline',
    'content_URL','publish_date','snippet_text','page_number','page_URL']
    fileExt='.csv'
    outputFile = 'gweb_' + fileExt
    writeHeader = True
    while True:
    	  soup = get_url_content(searchURL)
    	  if soup:
    	     contentList = scrap_page_content(soup)
    	  if contentList:
    	     write_to_csv(contentList, outputFile)
    
def get_url_content(myURL):
    waitTime = random.randrange(3,10,1)
    time.sleep(waitTime)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = requests.get(myURL, headers = headers)
    '''
    try:
        res.raise_for_status()
        soup = bs4.BeautifulSoup
    except Exception as exec:
    	logger.error('there was a problem: %s' %(exec))        
    	soup = ''
    logger.info('exiting:get_url_content')
    return soup
    '''
def scrap_page_content(soup):
    global searchURL
    result = []
    searchtext = searchURL.split('q=')[1].split('&')[0]
    searchText = searchText.encode('utf-8')
    startDateText = searchURL.split('cd_min:')[-1].split(',')[0]
    if not startDateText[-1].isdigit():
       startDateText = startDateText.split(',').[0]
    endDateText = searchURL.split('cd_max:')[-1].split('&')[0]
    try:
       currentPageNum = soup.find_all('td',{'class':'cur'}).get_text()
    except Exception as exc:
       logger.error('Page number not found: %s' % (exc))
       currentPageNum = ''
    #headerContent   
    headerName = soup.find_all('h3',{'class':'r'})[0].text

    headerURL = soup.find_all('h3', {'class':'r'})[0].find('a').get('href')
    
    source_URL = soup.find_all('cite',{'class':'_Rm'})[0].text

    bodyContent = soup.find_all('span',{'class':'st'})[0].text

    contentDate=bodyContent.split('-')[0]
    
    
    
    
    
    
    
    try:
       headerContent = soup.find_all('h3',{'class':'r'})
    except Exception as exc:
       logger.error('headerContent is not found:%s' % (exc)) 	
       headerContent = ''
       return result
    
    for contents in headerContent:
        try:
           headerText = headerContent.   
       
    try:
       bodyContents = soup.find_all('span',{'class':'st'})   
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
    
    
    
