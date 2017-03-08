#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 13:15:59 2017

"""

from lxml import etree
import logging
import configparser
import os
import sys
import sqlite3
from pathlib import Path
#import datetime
import time


def set_logging(mylogFile = '../logs/jiraxmlparse.log'):
    global log

    check_path_create_dir(mylogFile)

    #mylogFile = logFile
    # create logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(mylogFile)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    #ch.setLevel(logging.INFO)
    ch.setLevel(logging.DEBUG)
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

def read_global_constants(configFile = '../config/jiraxmlparse.ini'):
    log.debug('Entering read_global_constants')
    #if not os.path.isfile(configFile):
    if not Path(configFile).is_file():
       log.critical ('{}: config file not found. Exiting...'.format(configFile))
       sys.exit()

    #jiraXMLbackup = '/home/titu/Documents/data/20170302/entities.xml'
    global jiraXMLbackup
    global db_name
    global table_name

    global create_table_sqlstmt
    global find_dup_file_sqlstmt
    global check_if_file_available_sqlstmt

    config = configparser.ConfigParser()
    config.read(configFile)

    jiraXMLbackup = config.get('DEFAULT','JIRA_XML_BACKUP').strip()
    db_name = config.get('DEFAULT','db_name').strip()
    '''
    table_name = config.get('DEFAULT','table_name').strip()

    create_table_sqlstmt = config.get('DEFAULT','create_table_sqlstmt').strip()
    create_table_sqlstmt = create_table_sqlstmt.replace('\n', ' ')

    find_dup_file_sqlstmt = config.get('DEFAULT','find_dup_file_sqlstmt').strip()
    find_dup_file_sqlstmt = find_dup_file_sqlstmt.replace('\n', ' ')

    check_if_file_available_sqlstmt = config.get('DEFAULT','check_if_file_available_sqlstmt').strip()
    check_if_file_available_sqlstmt = check_if_file_available_sqlstmt.replace('\n', ' ')
    '''
    log.debug('Exiting read_global_constants')
    return


def check_path_create_dir(filePath):
    if os.name == 'posix' and filePath[0] == '~':
       p = Path(filePath).expanduser()
    else:
       p = Path(filePath)
    if not p.parent.is_dir():
       p.parent.mkdir(mode = 0o777, parents = True, exist_ok = True)

def get_plugins(xmlFile):
    log.debug('Entering get_plugins')
    startTag = '___ User Plugins ____________________________'
    #systemPluginTag = '___ System Plugins __________________________'
    stopTag = '_' * 25

    startCollecting = False
    userPluginCount = 0
    pluginList = []
    row = []
    header = ['Name', 'Version','Status','Vendor','Description']
    name = ''
    with open(xmlFile) as fh:
         for line in fh.readlines():
             #print (line)
             if line.strip() == startTag:
                startCollecting = True
                continue

             if startCollecting and stopTag in line.strip():
                print (line)
                break

             if startCollecting and line:
                if 'Number' in line.strip():
                   userPluginCount = line.split(':')[1].strip()
                elif 'Version' in line.strip():
                   version = line.split(':')[1].strip()
                elif 'Status' in line.strip():
                   status = line.split(':')[1].strip()
                elif 'Vendor' in line.strip():
                   vendor = line.split(':')[1].strip()
                elif 'Description' in line.strip():
                   description = line.split(':')[1].strip()
                   row = [name, version, status, vendor, description]
                   #print (row)
                   pluginList.append(row)
                   row = []
                else:
                   name = line.split(':')[0].strip()


    #print (userPluginCount)
    print (pluginList, len(pluginList))

    if not int(userPluginCount) == len(pluginList):
       print ('Error: total user plugin count "{}", does not match the count "{}" of plugin list extracted'.format(userPluginCount, len(pluginList)))

    if pluginList:
       pluginList.insert(0,header)

    log.debug('Exiting get_plugins')
    return(pluginList)

def get_core_app_properties(xmlFile):
    log.debug('Entering get_core_app_properties')
    startTag = '___ Core Application Properties ____________'
    #stopTag = '___ Application Properties _________________'
    stopTag = '_' * 25

    startCollecting = False
    propList = []

    header = ['Server ID', 'Base URL', 'Version', 'Installation Type', 'External User Management']

    with open(xmlFile) as fh:
         for line in fh.readlines():
             #print (line)
             if line.strip() == startTag:
                startCollecting = True
                continue

             if startCollecting and stopTag in line.strip():
                break

             if startCollecting and line:
                if 'Version' in line.strip():
                   version = line.split(':')[1].strip()
                elif 'Installation Type' in line.strip():
                   installationType = line.split(':')[1].strip()
                elif 'Server ID' in line.strip():
                   serverID = line.split(':')[1].strip()
                elif 'Base URL' in line.strip():
                   baseURL = ':'.join(line.split(':')[1:]).strip()
                elif 'External User Management' in line.strip():
                   externalUserManagement = line.split(':')[1].strip()
                   propList = [[serverID, baseURL, version, installationType, externalUserManagement]]
                   break

    if propList:
       propList.insert(0,header)

    print (propList)
    log.debug('Exiting get_core_app_properties')
    return(propList)

def get_db_stats(xmlFile):
    log.debug('Entering get_db_stats')
    startTag = '___ Database Statistics ____________________'
    #stopTag = '___ Upgrade History ________________________'
    stopTag = '_' * 25

    startCollecting = False
    propList = []

    header = ['Issues','Projects','Custom Fields','Workflows','Users','Groups','Attachments','Comments' ]

    with open(xmlFile) as fh:
         for line in fh.readlines():
             #print (line)
             if line.strip() == startTag:
                startCollecting = True
                continue

             if startCollecting and stopTag in line.strip():
                break

             if startCollecting and line:
                if 'Issues' in line.strip():
                   issueCount = line.split(':')[1].strip()
                elif 'Projects' in line.strip():
                   projectCount = line.split(':')[1].strip()
                elif 'Custom Fields' in line.strip():
                   customFieldCount = line.split(':')[1].strip()
                elif 'Workflows' in line.strip():
                   workflowCount = line.split(':')[1].strip()
                elif 'Users' in line.strip():
                   userCount = line.split(':')[1].strip()
                elif 'Groups' in line.strip():
                   groupCount = line.split(':')[1].strip()
                elif 'Attachments' in line.strip():
                   attachmentCount = line.split(':')[1].strip()
                elif 'Comments' in line.strip():
                   commentsCount = line.split(':')[1].strip()
                   propList = [[issueCount, projectCount, customFieldCount, workflowCount, userCount, groupCount, attachmentCount, commentsCount]]
                   break
    if propList:
       propList.insert(0,header)

    print (propList)
    log.debug('Exiting get_db_stats')
    return(propList)

def get_file_paths(xmlFile):
    log.debug('Entering get_file_paths')
    startTag = '___ File Paths _____________________________'
    stopTag = '_' * 25

    startCollecting = False
    propList = []

    header = ['JIRA Home','Attachment Path']

    with open(xmlFile) as fh:
         for line in fh.readlines():
             #print (line)
             if line.strip() == startTag:
                startCollecting = True
                continue

             if startCollecting and stopTag in line.strip():
                break

             if startCollecting and line:
                if 'JIRA Home' in line.strip():
                   jiraHome = line.split(':')[1].strip()
                elif 'Attachment Path' in line.strip():
                   attachment = line.split(':')[1].strip()
                   propList = [[jiraHome, attachment]]
                   break
    if propList:
       propList.insert(0,header)

    print (propList)
    log.debug('Exiting get_file_paths')
    return(propList)

def get_trusted_applications(xmlFile):
    log.debug('Entering get_trusted_applications')
    startTag = '___ Trusted Applications ___________________'
    stopTag = '_' * 25

    startCollecting = False
    propList = []

    header = ['Application Name' ]

    with open(xmlFile) as fh:
         for line in fh.readlines():
             #print (line)
             if line.strip() == startTag:
                startCollecting = True
                continue

             if startCollecting and stopTag in line.strip():
                break

             if startCollecting and line:
                if 'Instance Count' in line.strip():
                   instanceCount = line.split(':')[1].strip()
                else:
                   name = line.split(':')[0].strip()
                   propList.append([name])
                   break
    if propList:
       propList.insert(0,header)

    print (propList)
    log.debug('Exiting get_trusted_applications')
    return(propList)

def get_jira_attribs(jiraAttribs, xmlfile):
    log.debug('Entering get_jira_attribs')
    jiraAttribsD = {}
    tree = etree.parse(xmlfile)
    for attribute in jiraAttribs:
        entries = tree.findall(attribute)
        log.debug (attribute)
        header = []
        rows = []
        row = []
        for entry in entries:
            #log.debug(entry.attrib.keys())
            headerT = list(entry.attrib.keys())
            for col in headerT:
                if col not in header:
                   header.append(col)

        for entry in entries:
	        row = [None] * len(header)
	        for col in entry.attrib:
	            row[header.index(col)] = entry.attrib[col]
	        rows.append(row)

        if rows:
            rows.insert(0, header)
            log.debug(rows)

        jiraAttribsD[attribute] = rows


    log.debug('Exiting get_jira_attribs')
    return(jiraAttribsD)

def connect_db(dbName):
    log.debug('Entering connect_db')

    try:
        conn = sqlite3.connect(dbName)
    except Exception as e:
        log.error ('Error "{1}" while connecting to DB "{0}"'.format(dbName, e))
        sys.exit(1)

    log.debug('Exiting connect_db')
    return conn

def create_table(conn, tableName, colDetails):
    log.debug('Entering create_table')
    #conn = sqlite3.connect(dbName)
    colDetailIdx = {'colname':0, 'coltype':1}

    sqlStmt = 'CREATE TABLE IF NOT EXISTS {} ('.format(tableName)
    for colDetail in colDetails:
        sqlStmt += '\'{}\' {},'.format(colDetail[colDetailIdx['colname']], colDetail[colDetailIdx['coltype']])

    sqlStmt = sqlStmt[:-1]
    sqlStmt += ');'

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
    #sqlStmt = create_table_sqlstmt

    log.debug('SQL: {}'.format(sqlStmt))
    conn.execute(sqlStmt)
    #conn.close()
    log.debug('Exiting create_table')
    return

def select_rows(conn, sqlStmt):
    log.debug('Entering select_rows')
    resultL = []
    log.debug ('{}'.format(sqlStmt))
    #conn = sqlite3.connect(dbName)
    try:
       cursor = conn.execute(sqlStmt)
    except Exception as e:
       log.warn('{}: {}'.format(e, sqlStmt))
    else:
        for row in cursor:
            resultL.append(row)

    #conn.close()
    log.debug('Exiting select_rows')
    return resultL

def insert_update_rows(conn, sqlStmts):
    log.debug('Entering insert_update_rows')
    #conn = sqlite3.connect(dbName)

    for sqlStmt in sqlStmts:
        try:
           #print ('SQL: {}'.format(sqlStmt))
           conn.execute(sqlStmt)
        except Exception as e:
           log.error ('Exception "{}" on SQL: "{}"'.format(e, sqlStmt))

    conn.commit()
    #conn.close()
    log.debug('Exiting insert_update_rows')
    return

def gen_insert_SQLs(tableName, colsL, dataL):
    log.debug('Entering gen_insert_SQLs')
    sqls = []
    colString = ','.join('"{}"'.format(item) for item in colsL)

    for entry in dataL:
        dataString = ''
        for col in entry:
            if col:
               dataString += "'{}',".format(col)
            else:
               dataString += 'null,'

        dataString = dataString[:-1]

        sqlT = 'INSERT INTO {} ({}) VALUES({});'.format(tableName, colString, dataString)
        log.debug ('sqlS: {}'.format(sqlT))
        sqls.append(sqlT)
    log.debug('Exiting gen_insert_SQLs')
    return sqls

def compare_table_cols_inputCols(conn, tableName, inputCols):
    log.debug('Entering compare_table_cols_inputCols')
    sqlStmt = "PRAGMA table_info('{}')".format(tableName)
    rows = select_rows(conn, sqlStmt)
    tableCols = []
    plusCols = []
    #minusCols = []
    for row in rows:
        tableCols.append(row[1])
    
    plusCols = [col for col in inputCols if col not in tableCols]
    log.debug('Exiting compare_table_cols_inputCols')
    return (tableCols, plusCols)
    
def update_jira_details(conn, tableName, colNameType, dataL, appID):
    log.debug('Entering update_jira_details')

    create_table(conn, tableName, colNameType)
    colsL = [entry[0] for entry in colNameType]
  
    diffCols = compare_table_cols_inputCols(conn, tableName, colsL)

    if not diffCols[1]:
       for row in dataL:
           #update data rows for primary key
           row.insert(0,appID)
           row.insert(0,None)

       sqls = gen_insert_SQLs(tableName, colsL, dataL)
       insert_update_rows(dbConn, sqls)
    else:
       log.error('Table Cols: {}\nInput data Cols:{} differ'.format(diffCols[0], colsL))
       log.error('Input data Cols not present in Table: {}'.format(diffCols[1]))

    log.debug('Exiting update_jira_details')

def main():
    set_logging()
    log.debug('Entering main')
    global dbConn
    dateFormat = '%Y-%m-%d %H:%M:%S %Z'

    jiraAttribs = ['Group', 'Project', 'ProjectRole','SchemePermissions', 'SearchRequest', 'User', 'Version', 'Workflow', 'WorkflowScheme', 'CustomField', 'FieldConfigScheme']

    jiraTables = {
            'JIRA_APP_DETAIL': [['APP_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['ACTIVE_REC','INTEGER']],
            'JIRA_PLUGIN':[['PLUGIN_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_DB_STAT':[['DB_STAT_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_FILE_PATH':[['FILE_PATH_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_TRUSTED_APP':[['TRUSTED_APP_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_Group':[['GROUP_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_Project':[['PROJECT_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_ProjectRole':[['PROJECT_ROLE_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_SchemePermissions':[['SCHEME_PERMISSIONS_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_SearchRequest':[['SEARCH_REQUEST_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_User':[['USER_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_Version':[['VERSION_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_Workflow':[['WORKFLOW_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_WorkflowScheme':[['WORKFLOW_SCHEME_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_CustomField':[['CUSTOM_FIELD_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'JIRA_FieldConfigScheme':[['FIELD_CONFIG_SCHEME_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']]
            }

    read_global_constants()

    dbConn = connect_db(db_name)

    core_app_props = get_core_app_properties(jiraXMLbackup)
    #add current date to the parsing information
    core_app_props[0].append('PARSED_DATE')
    currentTime = time.strftime(dateFormat, time.localtime())
    core_app_props[1].append(currentTime)

    for col in core_app_props[0]:
        jiraTables['JIRA_APP_DETAIL'].append([col, 'TEXT'])

    serverID = core_app_props[1][core_app_props[0].index('Server ID')]
    #check if xml for the current jira has been parsed
    sqlStmt = 'SELECT APP_ID FROM JIRA_APP_DETAIL WHERE "Server ID" = \'{}\' AND ACTIVE_REC = 1;'.format(serverID) 
    appID = select_rows(dbConn, sqlStmt)

    if appID:
       #there is already one snapshot of the jira details saved for the server id
       # make this snapshot inactive and move forward to save the current one
       log.info('JIRA instance with Server ID: {} is already present in the DB with APP_ID: {}'.format(serverID, appID[0][0]))
       log.info('Making the record with APP_ID: {} inactive'.format(appID[0][0]))

       sqlUpdateStmt = 'UPDATE JIRA_APP_DETAIL SET ACTIVE_REC = 0 WHERE "Server ID" = \'{}\' AND ACTIVE_REC = 1;'.format(serverID) 
       insert_update_rows(dbConn, [sqlUpdateStmt])
       
       '''
       log.error('JIRA instance with Server ID: {} is already present in the DB with APP_ID: {}'.format(serverID, appID[0][0]))
       log.info('Review the data captured for the JIRA instance clean up the data before re-parsing. Exiting....')
       log.info('Closing DB connection')
       dbConn.close()
       sys.exit()
       '''
       
    isActive = 1
    update_jira_details(dbConn, 'JIRA_APP_DETAIL', jiraTables['JIRA_APP_DETAIL'], core_app_props[1:], isActive)
    appID = select_rows(dbConn, sqlStmt)

    if appID:
       appID = appID[0][0]
       log.info('APP ID: {}'.format(appID))

    db_stats = get_db_stats(jiraXMLbackup)
    for col in db_stats[0]:
        jiraTables['JIRA_DB_STAT'].append([col, 'TEXT'])

    update_jira_details(dbConn, 'JIRA_DB_STAT', jiraTables['JIRA_DB_STAT'], db_stats[1:], appID)

    plugins = get_plugins(jiraXMLbackup)
    for col in plugins[0]:
        jiraTables['JIRA_PLUGIN'].append([col, 'TEXT'])

    update_jira_details(dbConn, 'JIRA_PLUGIN', jiraTables['JIRA_PLUGIN'], plugins[1:], appID)

    filePaths = get_file_paths(jiraXMLbackup)
    for col in filePaths[0]:
        jiraTables['JIRA_FILE_PATH'].append([col, 'TEXT'])

    update_jira_details(dbConn, 'JIRA_FILE_PATH', jiraTables['JIRA_FILE_PATH'], filePaths[1:], appID)

    jiraAttribsD = get_jira_attribs(jiraAttribs, jiraXMLbackup)

    for tableName in jiraAttribsD.keys():
        for col in jiraAttribsD[tableName][0]:
            jiraTables['JIRA_'+tableName].append([col, 'TEXT'])

        #log.debug('Inserting for table {}'.format(tableName))
        update_jira_details(dbConn, 'JIRA_'+tableName, jiraTables['JIRA_'+tableName], jiraAttribsD[tableName][1:], appID)


    log.info('Closing DB connection')
    dbConn.close()
    log.debug('Exiting main')

main()
