
#!/usr/bin/python
# Usage: This script will save the contents of the URL to a local file

import requests
import sys

def saveURL(URLname, outFile):
    print 'Reading URL: {0}'.format(URLname)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    res = requests.get(URLname, headers = headers)
    res.raise_for_status()
    playFile = open(outFile, 'wb')
    for chunk in res.iter_content(100000):
        playFile.write(chunk)

    playFile.close()
    print 'Saved the URL to file: {0}'.format(outFile)

def main():
    if len(sys.argv) > 1:
       saveURL(sys.argv[1], sys.argv[2])
    else:
       print "Usage: script_name <URL> <outputFileName>"

main()
