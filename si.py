import requests
import time
import csv
import os.path
import random
import bs4
import re


content_headers = [
 u'Page URL',
 u'Reply',
 u'Message Preview',
 u'From',
 u'Recs',
 u'Posted',
 u'Message URL',
 u'Full Message',
 u'Sentiment',
 u'pos%',
 u'neg%',
 u'neutral%']
 
def main():
    print ('Entering main')
   
    global baseURL
    baseURL = 'http://www.siliconinvestor.com'
    subID = '58561' #Facebook

    global pageURL
    
    sourceURL = baseURL + '/subject.aspx?subjectid=' + subID
    outputFolder = '../output'
    fileExt = '.csv'
    
    dateFormat = '%Y%m%d_%H%M%S'
    outputFile = '{}/{}{}{}{}{}'.format(outputFolder, 'si_', subID, '_', time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time())), fileExt)
    startTime = time.time()
    

    writeHeader = True
    pgno = 0

    if not os.path.exists(outputFolder):
       os.makedirs(outputFolder)

    pageURL = sourceURL
    while True:
          # get data
          pageDataObj = read_url(pageURL)
      
          # if no data exit    
          if not pageDataObj:
             break 
             
          pageData = scrape_data(pageDataObj)
          
          # save data
          if writeHeader:
             writeHeader = False
             write_to_csv([content_headers], outputFile)
          
          write_to_csv(pageData, outputFile)       

          previousPageURL = get_prev_page_url(pageDataObj)
          
          if pgno == 10:
             break
             
          pgno += 1
          
          if not previousPageURL:
             break
          else:
             pageURL = previousPageURL
             
          
    print('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))

    print ('Exiting main')
         
def read_url(myURL, maxRetries = 1):
    print ('Entering read_url')
    bsObj = ''
 
    for tryCount in range(0, maxRetries):
    
        if tryCount > 0:
           print ('Retry count: {}'.format(tryCount +1))
           
        waitTime = random.randrange(3,10,1) * (tryCount + 1)
        print('Waiting for {0} seconds before hitting the URL'.format(waitTime))
        time.sleep(waitTime)

        print ('reading url: {}'.format(myURL))
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        res = requests.get(myURL, headers = headers)

        try:
           res.raise_for_status()
        except Exception as exc:
           print('There was a problem: %s' % (exc))
           bsObj = ''
        else:
            bsObj = bs4.BeautifulSoup(res.text, 'lxml')
            break
        
    print ('Exiting read_url')
    return bsObj

def scrape_data(bsObj):
    print ('Entering scrape_data')
    
    '''
    >>> bsobj.find('table', {'id':'grdMsgList'}).findAll('tr')[1].findAll('td')[1].text
    'No more buying enthusiasm but sellers not sure about the recent slow sell-off. B'
    '''
    resultList = []
    
    for row in bsObj.find('table', {'id':'grdMsgList'}).findAll('tr'):
        entryList = []
        for col in row.findAll('td'):
            value = col.text
            entryList.append(value)

        try:
           fullMsgURL = row.find('a').get('href')
        except Exception as exc:
           print('There was a problem: %s' % (exc))
           fullMsgURL = ''
           sentimentL = ['Message not available','','','']
        else:
           if fullMsgURL:
              fullMsgURL = baseURL + '/' + fullMsgURL
              pageDataObj = read_url(fullMsgURL)
              fullMsg = scrape_full_msg(pageDataObj)
           else:
              fulMsg = ''

           if fullMsg:
              sentimentL = find_sentiment(fullMsg)
           
           entryList.append(fullMsgURL)
           entryList.append(fullMsg)
           entryList = entryList + sentimentL
        
        if entryList:
           entryList = [pageURL] + entryList
           resultList.append(entryList)
           
    print ('Exiting scrape_data')
    return resultList


'''
>>> url2 = 'http://www.siliconinvestor.com/readmsg.aspx?msgid=30942292'
>>> res2 = requests.get(url2, headers = headers)
>>> bsobj2 = bs4.BeautifulSoup(res2.text, 'lxml')
>>> bsobj2.find('span', {'id':'intelliTXT'})
<span id="intelliTXT">No more buying enthusiasm but sellers not sure about the recent slow sell-off. Buying mood so far, but SS group can not bet ER.</span>
>>> bsobj2.find('span', {'id':'intelliTXT'}).text
'No more buying enthusiasm but sellers not sure about the recent slow sell-off. Buying mood so far, but SS group can not bet ER.'

'''
def scrape_full_msg(bsObj):
    print ('Entering scrape_full_msg')
    fullMsg = ''
    try:
       fullMsg = bsObj.find('span', {'id':'intelliTXT'}).text
    except Exception as exc:
       print('There was a problem: %s' % (exc))
       fullMsg = ''

    #print ('FullMsg: {}'.format(fullMsg))
    print ('Exiting scrape_full_msg')
    return fullMsg

def get_prev_page_url(bsObj):
    print ('Entering get_next_page_url')

    prevPageURL = ''
    prevPageText = bsObj.find('table', class_ = re.compile('text2b full')).find('a').text

    if 'Previous' in prevPageText:
        prevPageURL = bsObj.find('table', class_ = re.compile('text2b full')).find('a').get('href')
        prevPageURL = baseURL + '/' + prevPageURL

    return prevPageURL
    print ('Exiting get_next_page_url')

def find_sentiment(mytext):
    print ('Entering find_sentiment')
    sentimentURL = 'http://text-processing.com/api/sentiment/'
    data = {'text': mytext}
    res = requests.post(sentimentURL, data = data)
    #print ('Text: {}'.format(mytext))
    #dataDic = json.loads(res.text)
    sentimentL = ['','','','']

    try:
       dataDic = res.json()
    except Exception as exc:
       print (res.text)
       print('There was a problem: %s' % (exc))

    try:
       sentimentL = [dataDic['label'], dataDic['probability']['pos'], dataDic['probability']['neg'], dataDic['probability']['neutral']]
       print ('Text: {}{}Sentimet: {}'.format(mytext, '\n', dataDic['label']))
    except KeyError:
       print ('Text: {}'.format(mytext))
       print ('ERROR Response: {}'.format(res.text))
       
    print ('Exiting find_sentiment')
    return (sentimentL)
    
def write_to_csv(contentList, outputFile):
    print('Entering: write_to_csv')

    print('Writing to file: {0}'.format(outputFile))
    #print contentList

    with open(outputFile, 'a') as fh:
         csvWriter = csv.writer(fh, delimiter = ',', quoting = csv.QUOTE_ALL)
         csvWriter.writerows(contentList)

    print('Exiting: write_to_csv')
    

main()

