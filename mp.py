import requests
import bs4
import re
import json
import csv
import sys
import logging
from logging.handlers import RotatingFileHandler
import datetime
import random
import time

minWaitTime = 5
maxWaitTime = 7

csvHeader = [
 u'pluginNameSearched', 
 u'pluginNameFromAPI', 
 u'pluginURL',
 u'pluginNameFromMP',
 u'vendorName', 
 u'atlassianVerified', 
 u'pluginCompatibility', 
 u'supported', 
 u'dataCenterSupport', 
 u'pluginVersion', 
 u'application', 
 u'versionHistory', 
 u'releaseSummary', 
 u'totalPluginInstalls', 
 u'reviewCount', 
 u'ratingInpx']
 
def set_up_logging(LOGFILE):
 log = logging.getLogger('ap')
 log.setLevel(logging.DEBUG)
 format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

 ch = logging.StreamHandler(sys.stdout)
 ch.setFormatter(format)
 log.addHandler(ch)

 fh = RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=7)
 #fh = logging.FileHandler(LOGFILE)
 fh.setFormatter(format)
 log.addHandler(fh)
 
 return log

def get_plugin_url(pluginName):
 log.info('Entering get_plugin_url')
 data = {'q': pluginName}
 resultL = []
 validReturnCodes = [200]
 errorText = 'HTTP error'
 #https://marketplace.atlassian.com/rest/2/addons/search/brief?q=<text>
 marketplaceBaseURL = 'https://marketplace.atlassian.com'
 marketplaceRESTURL = '/rest/2/addons/search/brief'
 marketplaceURL = marketplaceBaseURL + marketplaceRESTURL + '?q=' + pluginName

 #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
 
 headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
 
 random.seed(datetime.datetime.now())
 time2wait = random.randint(minWaitTime,maxWaitTime)
 log.info('Waiting for {} seconds'.format(time2wait))
 time.sleep(time2wait)
 
 try:
  #page = requests.get(marketplaceURL, headers = headers, data = data)
  page = requests.get(marketplaceURL, headers = headers)
 except requests.exceptions.RequestException as e:
  # A serious problem happened, like an SSLError or InvalidURL
  log.error("Error: {}".format(e))
  resultL = [pluginName, errorText]
 else:
  log.info('{}: PageScrape rc: {}'.format(marketplaceURL, page.status_code))
  if page.status_code in validReturnCodes:
   log.info('JSON Resp: {}'.format(page.json()))
   if len(page.json()['addons']) > 0:
    for item in page.json()['addons']:
     pluginName = item['name']
     pluginURL = item['_links']['alternate']['href']
     pluginURL = pluginURL.replace('/overview', '/versionhistory') #get version history URL
     pluginURL = marketplaceBaseURL + pluginURL #get complete URL
     resultL.append([pluginName, pluginURL])

 
 log.info('Result MPapi: {}'.format(resultL))    
 log.info('Exiting get_plugin_url') 

 return resultL

def scrape_plugin_details(pluginURL):
 log.info('Entering scrape_plugin_details')
 resultL = []
 validReturnCodes = [200]
 errorText = 'HTTP error'
 
 random.seed(datetime.datetime.now())
 time2wait = random.randint(minWaitTime,maxWaitTime)
 log.info('Waiting for {} seconds'.format(time2wait))
 time.sleep(time2wait)
 
 try:
  page = requests.get(pluginURL)
 except requests.exceptions.RequestException as e:
  # A serious problem happened, like an SSLError or InvalidURL
  log.error("Error: {}".format(e))
  resultL = [errorText]
 else: 
  log.info('{}: PageScrape rc: {}'.format(pluginURL, page.status_code))
  
  if page.status_code in validReturnCodes:
   bsobj = bs4.BeautifulSoup(page.content, 'html.parser')

   # Release date
   versionHistory = ''
   
   #plugin name
   pluginName = return_text(bsobj.find('h1'))

   #vendor-name
   vendorName = return_text(bsobj.find('div', class_ = 'plugin-info').find('span', class_ = 'vendor-details').find('a', class_ = 'plugin-vendor-name'))

   #Atlassian verified?
   atlassianVerified = return_text(bsobj.find('div', class_ = 'plugin-info').find('span', class_ = 'vendor-details').find('a', class_ = re.compile('verified')))

   #plugin compatibility
   pluginCompatibility = return_text(bsobj.find('div', class_ = 'plugin-info').find('span', class_ = 'plugin-compatibility'))

   # Supported?
   supported = return_text(bsobj.find('div', class_ = 'plugin-support-info plugin-lozenge show-server').find('span', class_ = 'plugin-support-status aui-lozenge aui-lozenge-subtle'))

   # Data center support?
   dataCenterSupport = return_text(bsobj.find('div', class_ = 'plugin-support-info plugin-lozenge show-server').find('span', class_ = 'plugin-data-center aui-lozenge aui-lozenge-subtle'))

   # Plugin version
   pluginVersion = return_text(bsobj.find('section', {'data-tab-key':'versionhistory'}).find('span', class_ = 'version-name'))

   # Application
   application = return_text(bsobj.find('section', {'data-tab-key':'versionhistory'}).findAll('span', class_ = 'application'))

   # Release date
   dotSep = return_text(bsobj.find('section', {'data-tab-key':'versionhistory'}).find('span', class_ = 'dot'))
   if dotSep:
    versionHistory = return_text(bsobj.find('section', {'data-tab-key':'versionhistory'}).find('span', class_ = 'show-server'))
    if versionHistory:
     versionHistory = versionHistory.split(dotSep)[-1].strip()
     #bsobj.find('section', {'data-tab-key':'versionhistory'}).find('span', class_ = 'show-server').text.split(dotSep)[-1].strip()
    else:
     versionHistory = return_text(bsobj.find('section', {'data-tab-key':'versionhistory'}).find('span', class_ = 'show-cloud'))
     if versionHistory:
      versionHistory = versionHistory.split(dotSep)[-1].strip()

   # Release Summary
   releaseSummary = return_text(bsobj.find('div', id = 'release-summary').find('p'))
   releaseSummary = releaseSummary.replace('\u200b', '')

   # Total plugin installs
   totalPluginInstalls = return_text(bsobj.find('div', class_ = 'show-server').find('span', class_ = 'plugin-active-installs-total'))

   # Review count
   reviewCount = return_text(bsobj.find('span', class_ = 'badge'))

   # Rating
   rating = return_attr(bsobj.find('span', class_ = 'plugin-star-rating-inner'), 'style')
   rating = rating.split('width:')[-1].strip().replace('px;','')
   
   resultL =[pluginName, vendorName, atlassianVerified, pluginCompatibility, supported, dataCenterSupport, pluginVersion, application, versionHistory, releaseSummary, totalPluginInstalls, reviewCount, rating]
  
 log.info('Result PluginPage: {}'.format(resultL))
 log.info('Exiting scrape_plugin_details')
 return resultL

def return_text(markup):
 log.info('Entering return_text')
 text = ''
 if markup:
  if type(markup) is bs4.element.ResultSet:
   textL = []
   for item in markup:
    textL.append(item.text)
   text = ','.join(textL)
  else:
   text = markup.text
 log.info('Exiting return_text')
 return text

def return_attr(markup, attribute):
 log.info('Entering return_attr')
 text = ''
 log.info('markup: {}'.format(markup))
 log.info('attr: {}'.format(attribute))
 if markup:
    text = markup.get(attribute)

 log.info('Exiting return_attr') 
 return text
 
def process_plugin_list(inputFile):
 log.info('Entering process_plugin_list')
 pluginRespL = []
 resultL = []
 pluginRespDIdx = {
  'PLUGIN_NAME': 0,
  'PLUGIN_URL': 1
 }
 with open(inputFile) as fh:
  for pluginName in fh:
   pluginName = pluginName.strip()
   pluginRespsL = get_plugin_url(pluginName)
   if pluginRespsL:
    for pluginRespL in pluginRespsL:
     pluginDetails = scrape_plugin_details(pluginRespL[pluginRespDIdx['PLUGIN_URL']])
     resultL.append([pluginName] + pluginRespL + pluginDetails)
   else:
    resultL.append([pluginName])
    
 log.info('Exiting process_plugin_list')    
 return resultL

def write_csv(contentL, filename = 'out.csv'):
 log.info('Entering write_csv')
 with open(filename, 'w', newline='') as fh:
  csvwriter = csv.writer(fh)
  csvwriter.writerows(contentL) 
 log.info('Exiting write_csv')
 
def main():
 global log
 LOGFILE = 'logs/atlpl.txt'
 OUTFILE = 'output/atlpl2.csv'
 log = set_up_logging(LOGFILE)
 log.info('Entering main')
 startTime = time.time()
 inputFile = sys.argv[1]
 pluginDetailsL = process_plugin_list(inputFile)
 if pluginDetailsL:
  log.info('pluginDetailsL: {}'.format([csvHeader] + pluginDetailsL))
  write_csv([csvHeader] + pluginDetailsL, OUTFILE)
  #write_csv(pluginDetailsL, OUTFILE)
  log.info('OutputFile: {}'.format(OUTFILE))
 
 endTime = time.time()
 log.info('Total time taken to complete: {} seconds-------------------------------------------'.format(endTime - startTime))
 
 log.info('Exiting main')
main()
