import re
import requests
from bs4 import BeautifulSoup
searchURL = 'https://www.google.co.in/search?q=infosys stock news&client=ubuntu&channel=fs&biw=1095&bih=915&noj=1&tbs=cdr:1,cd_min:01/12/2013,cd_max:31/12/2014&ei=ZexAWJLdJcjwvgTN75nYBA&start=0&sa=N'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
resp = requests.get(searchURL, headers = headers)
soup = bs4.BeautifulSoup(resp.text, 'lxml')
get1 = soup.find('td',{'class':'cur'}).get_text
print get1
