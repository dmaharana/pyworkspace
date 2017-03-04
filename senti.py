import requests
import json
import csv
import sys

def find_sentiment(mytext):
    print ('Entering find_sentiment')
    url = 'http://text-processing.com/api/sentiment/'
    data = {'text': mytext}
    res = requests.post(url, data = data)
    print ('Text: {}'.format(mytext))
    #dataDic = json.loads(res.text)
    
    try:
       dataDic = res.json()
    except Exception as exc:
       print (res.text)
       print('There was a problem: %s' % (exc))

    try:
       sentimentL = [dataDic['label'], dataDic['probability']['pos'], dataDic['probability']['neg'], dataDic['probability']['neutral']]
    except KeyError:
       sentimentL = []
       
    print ('Exiting find_sentiment')
    return (sentimentL)
    
def process_csv(csvFile, textColName):
    print ('Entering process_csv')
    updatedCSV = []
    gotHeader = False
    textColNameIdx = 0
    newCols = ['sentiment', 'pos%', 'neg%', 'neutral%']
    resultCSV = csvFile.split('.csv')[-2]+'_sentiment.'+csvFile.split('.')[-1]
    
    
    with open(csvFile) as fh:
         csvreader = csv.reader(fh)
         for row in csvreader:
             if not gotHeader:
                textColNameIdx = row.index(textColName)
                updatedCSV.append(row + newCols)
                gotHeader = True
                continue
             if row[textColNameIdx]:
                sentimentL =  find_sentiment(row[textColNameIdx])
                if sentimentL:
                   updatedCSV.append(row + sentimentL)   
                else:
                   break
             else:
                 updatedCSV.append(row + ['No text available'])
                    
    if len(updatedCSV) > 1:
       with open(resultCSV , 'w') as fh:
            csvwriter = csv.writer(fh)
            csvwriter.writerows(updatedCSV)
       print ('Writing to file: {}'.format(resultCSV))      
    print ('Exiting process_csv')
             
def main():
    print ('Entering main')
    csvFile = sys.argv[1]
    textColName = 'full_message'
    process_csv(csvFile, textColName)
    
    print ('Exiting main')

main()
#nikki@nikki-Lenovo-G510:~/Documents/sentimentAnalysis/webscrapping/bin$ python senti.py ../output/'L&T_mc_20170117_170051.csv'

