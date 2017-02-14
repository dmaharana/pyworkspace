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
import configparser
import sys

def set_logging(mylogFile = 'pics.log'):
    global log
    
    #mylogFile = logFile
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
    
    return


def create_table(dbName, tableName):
    log.debug('Entering create_table')
    conn = sqlite3.connect(dbName)
    
    '''
    sqlStmt = 'CREATE TABLE IF NOT EXISTS {}\
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
    ABSFILENAME TEXT NOT NULL,\
    FILENAME TEXT NOT NULL,\
    FILECTIME TEXT NOT NULL,\
    FILEMTIME TEXT NOT NULL,\
    ENTRYDATE TEXT NOT NULL,\
    IMAGEHASH TEXT,\
    ERROR TEXT,\
    ACTIVE INTEGER NOT NULL);'.format(tableName)
    '''
    sqlStmt = create_table_sqlstmt

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
    log.debug ('{}'.format(sqlStmt))
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
   
    filesList = glob.glob(srcDir + '/*.' + imgExt)

    if not filesList:
       log.info('No files with extension: "{1}" found in dir: {0}'.format(srcDir, imgExt))
       
    for imagePath in filesList:
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
        ctime = time.strftime(date_format, time.localtime(ctime))

        mtime = os.path.getmtime(abspath)
        mtime = time.strftime(date_format, time.localtime(mtime))

        currentTime = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)

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
    '''
    sqlStmt = "select absfilename, imagehash from {0} \
               where active = 1 and imagehash in (select  imagehash as c from {0} \
               where error = '' and active = 1 group by imagehash \
               having count(0) > 1 order by imagehash) \
               order by imagehash".format(tableName)
    '''           
    sqlStmt = find_dup_file_sqlstmt
    
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
    #sqlStmt = 'select absfilename from {} where active = 1'.format(tableName)
    
    sqlStmt = check_if_file_available_sqlstmt
    
    #log.info(sqlStmt)
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
    log.debug('Entering write_to_csv')
    dirName = os.path.dirname(outputFile)
    if not os.path.isdir(dirName):
       log.info('Creating folder: {}'.format(dirName))
       os.makedirs(dirName)
       
    with open(outputFile, 'w') as fh:
         log.info('CSV created: {}'.format(outputFile))
         csvWriter = csv.writer(fh)
         csvWriter.writerows(rowsL)
    
    log.debug('Exiting write_to_csv')
    return

def read_global_constants(configFile):
    log.debug('Entering read_global_constants')
    if not os.path.isfile(configFile):
       log.critical ('{}: config file not found. Exiting...'.format(configFile))
       sys.exit()
       
    global date_format
    #dateFormat = '%Y-%m-%d %H:%M:%S'    
    global img_dir
    global trash_dir
    global clean_dup
    global csv_header 
    global output_dir 
    global img_ext
    global db_name
    global table_name
    
    global create_table_sqlstmt
    global find_dup_file_sqlstmt
    global check_if_file_available_sqlstmt
    
    config = configparser.ConfigParser()
    config.read(configFile)

    date_format = config.get('DEFAULT','DATE_FORMAT').strip()
    img_dir = config.get('DEFAULT','img_dir').strip()
    trash_dir = config.get('DEFAULT','trash_dir').strip()
    clean_dup = False
    if config.get('DEFAULT','clean_dup').strip().lower() in 'yes':
       clean_dup = True
    csv_header = config.get('DEFAULT','csv_header').strip().split(',')
    output_dir = config.get('DEFAULT','output_dir').strip()
    img_ext = config.get('DEFAULT','img_ext').strip()
    db_name = config.get('DEFAULT','db_name').strip()
    table_name = config.get('DEFAULT','table_name').strip()
    
    create_table_sqlstmt = config.get('DEFAULT','create_table_sqlstmt').strip()
    create_table_sqlstmt = create_table_sqlstmt.replace('\n', ' ')
    
    find_dup_file_sqlstmt = config.get('DEFAULT','find_dup_file_sqlstmt').strip()
    find_dup_file_sqlstmt = find_dup_file_sqlstmt.replace('\n', ' ')
    
    check_if_file_available_sqlstmt = config.get('DEFAULT','check_if_file_available_sqlstmt').strip()
    check_if_file_available_sqlstmt = check_if_file_available_sqlstmt.replace('\n', ' ')
    
    log.debug('Exiting read_global_constants')
    return
    
def main():
    
    set_logging()
    
    log.debug('Entering main')    
    configFile = 'picconfig.ini'
    read_global_constants(configFile)
    
    startTime = time.time()
    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
    #rootDir = '/home/titu/Downloads/tfiles/temp/pics'
    #rootDir = '/media/mm/Documents/temp/pics/temp/sep07/draw'
    #rootDir = '/home/titu/Pictures'
    rootDir = img_dir
    #trashFolder = '/home/titu/Downloads/tfiles/temp/pics/trash'
    #trashFolder = rootDir + '/trash'
    trashFolder = trash_dir
    cleanDup = clean_dup
    
    #csvHeader = ['DHASH_VALUE', 'ORIGINAL_FILE','DUPLICATE_FILE(S)']
    csvHeader = csv_header
    #ouputFile = 'output/dupImg_{}.csv'.format(currentTime)
    ouputFile = '{}/dupImg_{}.csv'.format(output_dir, currentTime)
    
    #imgExt = 'png'
    #dbName = 'imageDB.db'
    #tableName = 'IMGFILEHASH5'
    
    imgExt = img_ext
    dbName = db_name
    tableName = table_name
    
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
