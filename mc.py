import requests
import json
import time
import csv
import os.path
import random
import codecs
import unicodedata

content_headers = [
 u'topic_url',
 u'is_redis',
 u'following_count',
 u'msg_id',
 u'rank',
 u'thread_id',
 u'message',
 u'topicid',
 u'user_id',
 u'category_url',
 u'ent_date',
 u'follower_count',
 u'str_posted_via',
 u'checked',
 u'msg_reply_count',
 u'repost_date',
 u'msg_url',
 u'repost_by_user_url',
 u'price',
 u'user_id_hex',
 u'average',
 u'msg_thread_url',
 u'full_message',
 u'heading',
 u'tp_category']
 
def main():
    print ('Entering main')
    offset = 160
    isp = 1
    tid = 148716 #for TCS
    pgno = 17
    scrappedJson = []
    outputFolder = '../output'
    fileExt = '.csv'
    
    dateFormat = '%Y%m%d_%H%M%S'
    #outputFile = outputFolder + '/' + 'mc_' + str(int(time.time()))+fileExt
    outputFile = '{}/{}{}{}'.format(outputFolder, 'mc_', time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time())), fileExt)
    startTime = time.time()
    

    writeHeader = True

    if not os.path.exists(outputFolder):
       os.makedirs(outputFolder)

    while True:
          url = 'http://mmb.moneycontrol.com/index.php?q=topic/ajax_call&section=get_messages&is_topic_page=1&offset={}&lmid=&isp={}&gmt=tp_lm&tid={}&pgno={}'.format(offset, isp, tid, pgno) 

          # get data
          scrappedJson = read_url(url)
      
          # if no data exit    
          if not scrappedJson:
             break 
             
          pageData = scrape_data(scrappedJson)
          
          # save data
          if writeHeader:
             writeHeader = False
             write_to_csv([content_headers], outputFile)
          
          write_to_csv(pageData, outputFile)       
          
          
          if pgno == 19:
             break
             
          if not offset:
             offset = 0
          offset += 10
          isp = 1
          pgno += 1
          
    print('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))

    print ('Exiting main')
         
def read_url(myURL, maxRetries = 3):
    print ('Entering read_url')
 
    for tryCount in range(0, maxRetries):
    
        if tryCount > 0:
           print ('Retry count: {}'.format(tryCount +1))
           
        waitTime = random.randrange(3,10,1) * (tryCount + 1)
        print('Waiting for {0} seconds before hitting the URL'.format(waitTime))
        time.sleep(waitTime)

        print ('reading url: {}'.format(myURL))
        resData = []
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        res = requests.get(myURL, headers = headers)

        try:
           res.raise_for_status()
        except Exception as exc:
           print('There was a problem: %s' % (exc))
        else:
            resData = json.loads(res.text)
            break
        
    print ('Exiting read_url')
    return resData



def scrape_data(jasonList):
    conversion = {
    '\u2105':'%'
    }
    value = ''
    
    print ('Entering scrape_data')
    resultList = []
    for item in jasonList:
        entryList = []
        for header in content_headers:
            #value = unicodedata.normalize("NFKD", u(item[header]))
            value = item[header]
            
            #print 'Checking: {}'.format(value)
            
            if isinstance(value,str):
               print ('{}={}'.format(header, item[header]))
               '''
               value = unicodedata.normalize("NFKD", item[header])
               '''
               try:
                  value = value.encode('utf-8')
                  print 'encoded successfully: {}'.format(value)
               except UnicodeEncodeError:
                  print ''.format(value)
                  unic = u''
                  unic += value
                  value = unic
                  print 'Value = {}'.format(value)
                  
                
            '''
            try:
                value = str(item[header]).encode('utf-8', errors="ignore")
                #value = unicode(str(item[header]), "utf-8", errors="ignore")	
            except UnicodeEncodeError:
                print ('Error encoding:[{}] {}'.format(header, item))
                value = str(item[header]).encode('ascii', 'ignore').decode('ascii')
            '''
            
            entryList.append(value)
            
        resultList.append(entryList)
           
    print ('Exiting scrape_data')
    return resultList

def write_to_csv(contentList, outputFile):
    print('Entering: write_to_csv')

    print('Writing to file: {0}'.format(outputFile))
    #print contentList

    with open(outputFile, 'ab') as fh:
         csvWriter = csv.writer(fh, delimiter = ',', quoting = csv.QUOTE_ALL)
         csvWriter.writerows(contentList)

    print('Exiting: write_to_csv')
    

main()

