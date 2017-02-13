import sqlite3
from PIL import Image
import imagehash
import glob
import os.path
import time
import datetime
import collections

dateFormat = '%Y-%m-%d %H:%M:%S'

def create_table(dbName):
    conn = sqlite3.connect(dbName)

    sqlStmt = ''' CREATE TABLE IF NOT EXISTS IMGFILEHASH
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ABSFILENAME TEXT UNIQUE,
    FILENAME TEXT NOT NULL,
    FILECTIME TEXT NOT NULL,
    FILEMTIME TEXT NOT NULL,
    ENTRYDATE TEXT NOT NULL,
    IMAGEHASH TEXT,
    ERROR TEXT);'''

    conn.execute(sqlStmt)
    conn.close()
    return

def insert_rows(dbName, sqlStmts):
    conn = sqlite3.connect(dbName)

    for sqlStmt in sqlStmts:
        try:
           #print ('SQL: {}'.format(sqlStmt))
           conn.execute(sqlStmt)
        except Exception as e:
           print ('Exception "{}" on SQL: "{}"'.format(e, sqlStmt))

    conn.commit()
    conn.close()
    return

def perform_select(dbName, sqlStmt):
    resultL = []
    conn = sqlite3.connect(dbName)
    cursor = conn.execute(sqlStmt)

    for row in cursor:
        resultL.append(row)

    conn.close()
    return resultL

def generate_image_dhash_value(srcDir, imgExt):
    resultL = []
    error = ''

    for imagePath in glob.glob(srcDir + '/*.' + imgExt):
        abspath = os.path.abspath(imagePath)
        filename = os.path.basename(abspath)

        ctime = os.path.getctime(abspath)
        ctime = time.strftime(dateFormat, time.localtime(ctime))

        mtime = os.path.getmtime(abspath)
        mtime = time.strftime(dateFormat, time.localtime(mtime))

        currentTime = datetime.datetime.fromtimestamp(time.time()).strftime(dateFormat)

        try:
           image = Image.open(abspath)
           h = str(imagehash.dhash(image))
        except Exception as e:
           print ('Exception "{}" on reading file "{}"'.format(e, abspath))
           h = ''
           error = e
        else:
           error = ''
        
        tempL = [abspath, filename, ctime, mtime, currentTime, h, error]
        resultL.append(tempL)

    return resultL

def gen_insert_SQLs(tableName, dataL):
    sqls = []
    for entry in dataL:
        dataString = ','.join('"{}"'.format(item) for item in entry)
        #print ('dataS: {}'.format(dataString))
        sqlT = 'INSERT INTO {} VALUES(null,{});'.format(tableName, dataString)
        #print ('sqlS: {}'.format(sqlT))
        sqls.append(sqlT)
    
    return sqls

def find_duplicate_files(dbName):
    sqlStmt = "select filename, imagehash from IMGFILEHASH where imagehash in (select  imagehash as c from IMGFILEHASH where error = '' group by imagehash having count(0) > 1 order by imagehash) order by imagehash"
    resultDict = collections.OrderedDict()
    resultL = perform_select(dbName, sqlStmt)
    for row in resultL:
        if row[1] in resultDict:
            resultDict[row[1]].append(row[0]) 
        else:
            resultDict[row[1]] = [row[0]]
    
    return resultDict
    
def main():
    rootDir = '/home/titu/Downloads/tfiles/temp/pics'
    imgExt = 'jpg'
    dbName = 'imageDB.db'
    tableName = 'IMGFILEHASH'

    create_table(dbName)
    
    imgData = generate_image_dhash_value(rootDir, imgExt)
    sqls = gen_insert_SQLs(tableName, imgData)
    insert_rows(dbName, sqls)
    
    dupFileD = find_duplicate_files(dbName)
    
    for hashVal, filenames in dupFileD.items():
        print ('{}:{}'.format(hashVal, filenames))
    
main()
