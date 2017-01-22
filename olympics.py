from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import re

outputFile = 'olympics.csv'
csvL = []

headerRow0 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
headerRow1 = ['','№ Summer', '01 :', '02 :', '03 :', 'Total', '№ Winter', '01 :', '02 :', '03 :', 'Total', '№ Games', '01 :', '02 :', '03 :', 'Combined total']
csvL.append(headerRow0)
csvL.append(headerRow1)

URL = 'https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table'
html = urlopen(URL)
bsObj = BeautifulSoup(html.read(), 'lxml')

tableH = bsObj.find('table', class_ = re.compile('wikitable'))

for row in tableH.findAll('tr'):
    cols = row.findAll('td')
    rowL = []
    if len(cols) > 0:
       for col in cols:
           rowL.append(col.text)
    if rowL:
       csvL.append(rowL)

with open(outputFile, 'w') as fh:
	 csvWriter = csv.writer(fh)
	 csvWriter.writerows(csvL)