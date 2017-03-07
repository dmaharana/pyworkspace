#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 13:15:59 2017

"""

from lxml import etree
import logging
import configparser
import os.path
import sys
import sqlite3



def read_global_constants(configFile = '../config/jiraxmlparse.ini'):
    log.debug('Entering read_global_constants')
    if not os.path.isfile(configFile):
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

def set_logging(mylogFile = '../logs/jiraxmlparse.log'):
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

def get_plugins(xmlFile):
    startTag = '___ User Plugins ____________________________'
    #systemPluginTag = '___ System Plugins __________________________'
    stopTag = '_' * 25

    startCollecting = False
    userPluginCount = 0
    pluginList = []
    row = []
    header = ['Name', 'Number','Version','Status','Vendor','Description']
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


    if pluginList:
       pluginList.insert(0,header)
    #print (userPluginCount)
    print (pluginList, len(pluginList))

    if not int(userPluginCount) == len(pluginList):
       print ('Error: total user plugin count "{}", does not match the count "{}" of plugin list extracted'.format(userPluginCount, len(pluginList)))

    return(pluginList)

def get_core_app_properties(xmlFile):
    startTag = '___ Core Application Properties ____________'
    #stopTag = '___ Application Properties _________________'
    stopTag = '_' * 25

    startCollecting = False
    propList = []

    header = ['Version','Installation Type','Server ID','Base URL','External User Management']

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
    return(propList)

def get_db_stats(xmlFile):
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
    return(propList)

def get_file_paths(xmlFile):
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
    return(propList)

def get_trusted_applications(xmlFile):
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
    return(propList)

def get_jira_attribs(jiraAttribs, xmlfile):

    jiraAttribsD = {}
    tree = etree.parse(xmlfile)
    for attribute in jiraAttribs:
        entries = tree.findall(attribute)
        print (attribute)
        header = []
        for entry in entries:
            print(entry.attrib.keys())
            header = list(entry.attrib.keys())

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

    conn.execute(sqlStmt)
    conn.close()
    log.debug('Exiting create_table')
    return

def select_rows(conn, sqlStmt):
    log.debug('Entering select_rows')
    resultL = []
    log.debug ('{}'.format(sqlStmt))
    #conn = sqlite3.connect(dbName)
    cursor = conn.execute(sqlStmt)

    for row in cursor:
        resultL.append(row)

    conn.close()
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
    conn.close()
    log.debug('Exiting insert_update_rows')
    return

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

'''
get_plugins(jiraXMLbackup)

get_db_stats(jiraXMLbackup)
get_file_paths(jiraXMLbackup)

get_jira_attribs(jiraXMLbackup)

get_core_app_properties(jiraXMLbackup)
'''

def main():
    log.debug('Entering main')

    jiraAttribs = ['Group', 'Project', 'ProjectRole','SchemePermissions', 'SearchRequest', 'User', 'Version', 'Workflow', 'WorkflowScheme', 'CustomField', 'FieldConfigScheme']

    jiraTables = {
            'APP_DETAIL': [['APP_ID','INTEGER PRIMARY KEY AUTOINCREMENT']],
            'PLUGIN':[['PLUGIN_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'DB_STAT':[['DB_STAT_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'FILE_PATH':[['FILE_PATH_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'TRUSTED_APP':[['TRUSTED_APP_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'Group':[['GROUP_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'Project':[['PROJECT_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'ProjectRole':[['PROJECT_ROLE_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'SchemePermissions':[['SCHEME_PERMISSIONS_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'SearchRequest':[['SEARCH_REQUEST_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'User':[['USER_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'Version':[['VERSION_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'Workflow':[['WORKFLOW_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'WorkflowScheme':[['WORKFLOW_SCHEME_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'CustomField':[['CUSTOM_FIELD_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']],
            'FieldConfigScheme':[['FIELD_CONFIG_SCHEME_ID','INTEGER PRIMARY KEY AUTOINCREMENT'],['APP_ID','INTEGER']]
            }

    set_logging()
    read_global_constants()

    dbConn = connect_db(db_name)

    core_app_props = get_core_app_properties(jiraXMLbackup)
    for col in core_app_props[0]:
        jiraTables['APP_DETAIL'].append([col, 'TEXT'])

    jira_attribs = get_jira_attribs(jiraAttribs, jiraXMLbackup)

    '''
    for tableName in jira_attribs:
        for col in jira_attribs[tableName][0]:
            jiraTables[tableName].append([col, 'TEXT'])

    db_stats = get_db_stats(jiraXMLbackup)
    for col in db_stats[0]:
        jiraTables['DB_STAT'].append([col, 'TEXT'])

    plugins = get_plugins(jiraXMLbackup)
    for col in plugins[0]:
        jiraTables['PLUGIN'].append([col, 'TEXT'])

    filePaths = get_file_paths(jiraXMLbackup)
    for col in filePaths[0]:
        jiraTables['FILE_PATH'].append([col, 'TEXT'])

    for tableName in jiraTables:
        create_table(dbConn, tableName, jiraTables[tableName])

    '''
    log.debug('Exiting main')

main()
