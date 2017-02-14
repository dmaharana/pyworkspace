import sqlite3
from PIL import Image
import imagehash
import glob
import os.path
import time
import datetime
import collections
import shutil
import logging
import os
import csv

mylogFile = 'pics.log'
# create logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(mylogFile)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -  %(funcName)s - %(lineno)s - %(message)s')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -  %(funcName)20s() - %(lineno)s - %(message)s')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(fh)
log.addHandler(ch)

dateFormat = '%Y-%m-%d %H:%M:%S'

def create_table(dbName, tableName):
    log.debug('Entering create_table')
    conn = sqlite3.connect(dbName)
    
    sqlStmt = 'CREATE TABLE IF NOT EXISTS {}\
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
    ABSFILENAME TEXT UNIQUE,\
    FILENAME TEXT NOT NULL,\
    FILECTIME TEXT NOT NULL,\
    FILEMTIME TEXT NOT NULL,\
    ENTRYDATE TEXT NOT NULL,\
    IMAGEHASH TEXT,\
    ERROR TEXT,\
    ACTIVE INTEGER NOT NULL,\
    UNIQUE (ABSFILENAME, ACTIVE));'.format(tableName)

    conn.execute(sqlStmt)
    conn.close()
    log.debug('Exiting create_table')
    return

def insert_update_rows(dbName, sqlStmts):
    log.debug('Entering insert_update_rows')
    conn = sqlite3.connect(dbName)

    for sqlStmt in sqlStmts:
        try:
           #print ('SQL: {}'.format(sqlStmt))
           conn.execute(sqlStmt)
        except Exception as e:
           log.error ('Exception "{}" on SQL: "{}"'.format(e, sqlStmt))

    conn.commit()
    conn.close()
    log.debug('Exiting insert_update_rows')
    return

def select_rows(dbName, sqlStmt):
    log.debug('Entering select_rows')
    resultL = []
    #log.debug ('{}'.format(sqlStmt))
    conn = sqlite3.connect(dbName)
    cursor = conn.execute(sqlStmt)

    for row in cursor:
        resultL.append(row)

    conn.close()
    log.debug('Exiting select_rows')
    return resultL

def generate_image_dhash_value(srcDir, imgExt, dbName, tableName):
    log.debug('Entering generate_image_dhash_value')
    resultL = []
    error = ''

    for imagePath in glob.glob(srcDir + '/*.' + imgExt):
        abspath = os.path.abspath(imagePath)
        
        sqlStmt = 'select count(0) from {} where active = 1 and absfilename ="{}"'.format(tableName,abspath)
        count = select_rows(dbName, sqlStmt)
        count = int(count[0][0])
        #print ('count: {}'.format(count))
        
        if count > 0:
           continue
           log.info ('skipping file: {}'.format(abspath))
           
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
           log.error ('Exception "{}" on reading file "{}"'.format(e, abspath))
           h = ''
           error = e
        else:
           error = ''
        
        tempL = [abspath, filename, ctime, mtime, currentTime, h, error]
        resultL.append(tempL)
    log.debug('Exiting generate_image_dhash_value')
    return resultL

def gen_insert_SQLs(tableName, dataL):
    log.debug('Entering gen_insert_SQLs')
    sqls = []
    for entry in dataL:
        dataString = ','.join('"{}"'.format(item) for item in entry)
        #print ('dataS: {}'.format(dataString))
        sqlT = 'INSERT INTO {} VALUES(null,{},{});'.format(tableName, dataString, 1)
        #print ('sqlS: {}'.format(sqlT))
        sqls.append(sqlT)
    log.debug('Exiting gen_insert_SQLs')
    return sqls

def find_duplicate_files(dbName, tableName):
    log.debug('Entering find_duplicate_files')
    sqlStmt = "select absfilename, imagehash from {0} \
               where active = 1 and imagehash in (select  imagehash as c from {0} \
               where error = '' and active = 1 group by imagehash \
               having count(0) > 1 order by imagehash) \
               order by imagehash".format(tableName)
    resultDict = collections.OrderedDict()
    resultL = select_rows(dbName, sqlStmt)
    for row in resultL:
        if row[1] in resultDict:
            resultDict[row[1]].append(row[0]) 
        else:
            resultDict[row[1]] = [row[0]]
    log.debug('Exiting find_duplicate_files')
    return resultDict

def check_files_present(dbName, tableName):
    log.debug('Entering check_files_present')
    sqlStmt = 'select absfilename from {} where active = 1'.format(tableName)
    activeFilesL = select_rows(dbName, sqlStmt)
    
    for row in activeFilesL:
        #print (row[0])
        if not os.path.isfile(row[0]):
           #update file not present row's active column to 0
           log.info ('{}: Not available'.format(row[0]))
           sqlStmt = 'update {} set active = 0 where absfilename = "{}"'.format(tableName, row[0])
           insert_update_rows(dbName, [sqlStmt])
    
    #print ('TotalLen: {}'.format(len(activeFilesL)))
    log.debug('Exiting check_files_present')
    return activeFilesL

def move_files(filesL, targetFolder, dbName, tableName):
    log.debug('Entering move_files')
    if not os.path.isdir(targetFolder):
       os.makedirs(targetFolder)
    
    for file in filesL:
        try:
           shutil.move(file, targetFolder)
        except Exception as e:
           log.error ('{}: Could not move "{}" into "{}"'.format(e, file, targetFolder))
        else:
           log.info ('Moved "{}" into "{}"'.format(file, targetFolder))
           sqlStmt = 'update {} set active = 0 where absfilename = "{}"'.format(tableName, file)
           insert_update_rows(dbName, [sqlStmt])
           
    log.debug('Exiting move_files')
    return

def write_to_csv(outputFile, rowsL):
    dirName = os.path.dirname(outputFile)
    if not os.path.isdir(dirName):
       log.info('Creating folder: {}'.format(dirName))
       os.makedirs(dirName)
       
    with open(outputFile, 'w') as fh:
         log.info('CSV created: {}'.format(outputFile))
         csvWriter = csv.writer(fh)
         csvWriter.writerows(rowsL)
    
    
def main():
    log.debug('Entering main')
    startTime = time.time()
    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime(dateFormat)
    #rootDir = '/home/titu/Downloads/tfiles/temp/pics'
    rootDir = '/media/mm/Documents/temp/pics/temp/sep07/draw'
    #trashFolder = '/home/titu/Downloads/tfiles/temp/pics/trash'
    trashFolder = rootDir + '/trash'
    cleanDup = True
    
    csvHeader = ['DHASH_VALUE', 'ORIGINAL_FILE','DUPLICATE_FILE(S)']
    ouputFile = 'output/dupImg_{}.csv'.format(currentTime)
    
    imgExt = 'jpg'
    dbName = 'imageDB.db'
    tableName = 'IMGFILEHASH4'
    
    resultsL = []
    
    dupFiles = []
    create_table(dbName, tableName)
    
    check_files_present(dbName, tableName)
    
    
    imgData = generate_image_dhash_value(rootDir, imgExt, dbName, tableName)
    
    if imgData:
       sqls = gen_insert_SQLs(tableName, imgData)
       insert_update_rows(dbName, sqls)
    
    dupFileD = find_duplicate_files(dbName, tableName)
    
    if dupFileD:
       log.info ('Duplicate files............')
       for hashVal, filenames in dupFileD.items():
           keepFile = min(filenames, key = len)
           filenames.remove(keepFile)
           delFiles = '\n'.join(filenames)
           dupFiles.extend(filenames)
           log.info ('{},{},{}'.format(hashVal, keepFile, delFiles))
           resultsL.append([hashVal, keepFile, delFiles])
    
    if resultsL:
       resultsL.insert(0,csvHeader)
       write_to_csv(ouputFile, resultsL)
     
    
    if dupFiles: 
       if cleanDup:
          move_files(dupFiles, trashFolder, dbName, tableName)
    else:
       log.info('{}: No duplicate images'.format(rootDir))
    
    log.info('Time taken: -------- {0} seconds ----------'.format(str(time.time() - startTime)))
    
    log.debug('Exiting main')
    return

main()
