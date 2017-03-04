#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 13:15:59 2017

@author: titu
"""

from lxml import etree

jiraXMLbackup = '/home/titu/Documents/data/20170302/entities.xml'

def get_plugins(xmlFile):
    startTag = '___ User Plugins ____________________________'
    #systemPluginTag = '___ System Plugins __________________________'
    stopTag = '_' * 25
    
    startCollecting = False
    userPluginCount = 0
    pluginList = []
    row = []
    header = ['Name', 'Number','Version','Status','Vendor','Description']
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
        
    header = ['JIRA Home','Attachment Path' ]
    
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

def get_jira_attribs(xmlfile):
    jiraAttribs = ['Group', 'Project', 'ProjectRole','SchemePermissions', 'SearchRequest', 'User', 'Version', 'Workflow', 'WorkflowScheme', 'CustomField', 'FieldConfigScheme']
    tree = etree.parse(jiraXMLbackup)    
    for attribute in jiraAttribs:
        entries = tree.findall(attribute)
        print (attribute)
        for entry in entries:
            print(entry.attrib.keys())



'''
get_plugins(jiraXMLbackup)

get_db_stats(jiraXMLbackup)
get_file_paths(jiraXMLbackup)
'''
get_jira_attribs(jiraXMLbackup)

get_core_app_properties(jiraXMLbackup)
