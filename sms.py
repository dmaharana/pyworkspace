import csv
import sys
import time
import bs4

'''
<sms address="+919538925264" body="I hosted the bridge. " contact_name="Sumathi" date="1406807858071" date_sent="1406807856000" locked="0" protocol="0" read="1" readable_date="Jul 31, 2014 5:27:38 PM" sc_toa="null" service_center="+919886005333" status="-1" subject="null" toa="null" type="1"></sms>
'''
sms_attrs = [
'address',
'body',
'contact_name',
'date',
'date_sent',
'locked',
'protocol',
'read',
'readable_date',
'sc_toa',
'service_center',
'status',
'subject',
'toa',
'type']

def capture_sms_data(smsxml):
    print('Entering: capture_sms_data')
    resultL = []
    bsobj = bs4.BeautifulSoup(open(smsxml), 'lxml')
    for item in bsobj.findAll('sms'):
        sms_content = []
        for attr in sms_attrs:
            sms_content.append(item.get(attr))
        if sms_content:
           resultL.append(sms_content)

    print('Exiting: capture_sms_data')
    
    return resultL

def write_to_csv(contentList, outputFile):
    print('Entering: write_to_csv')

    print('Writing to file: {0}'.format(outputFile))
    #print contentList

    with open(outputFile, 'a') as fh:
         csvWriter = csv.writer(fh, delimiter = ',', quoting = csv.QUOTE_ALL)
         csvWriter.writerows(contentList)

    print('Exiting: write_to_csv')
    
def main():
    print ('Entering main')
    
    inputFile = sys.argv[1]
    outputFolder = '../output'
    fileExt = '.csv'
    
    dateFormat = '%Y%m%d_%H%M%S'
    outputFile = '{}/{}{}{}'.format(outputFolder, 'sms_', time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time())), fileExt)
    
    smsData = capture_sms_data(inputFile)
    if smsData:
       smsData = [sms_attrs] + smsData
       write_to_csv(smsData, outputFile)
       print('SMS data saved to: {}'.format(outputFile))
    
    print ('Exiting main')
    
main()
