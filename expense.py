#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 14:08:27 2017

@author: titu
"""
import csv
import logging
import os
import os.path

inputFile = '/home/titu/Downloads/expenses.csv'

def set_logging(mylogFile = 'expense.log'):
    global log
    
    #mylogFile = logFile
    # create logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    
    # create file handler which logs even debug messages
    fh = logging.FileHandler(mylogFile)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    #formatter = logging.Formatter('%(levelname)s -  %(funcName)s - %(lineno)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -  %(funcName)s - %(lineno)s - %(message)s')
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -  %(funcName)20s() - %(lineno)s - %(message)s')
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    
    return

def extract_category(inputFile):
    categoryListing = {
        'Surcharge Dt:11':'Misc', 
        'TRF TO FD no. 004713024670':'Saving',
        'Dt:04':'Misc', 
        'ATD':'Misc', 
        'RwdRdmFee':'Misc', 
        'ATM':'Cash', 
        'To RD Ac no 004725028463':'Saving', 
        'Dr Tran For Funding A':'Trading', 
        'TRF TO FD no. 004713024576':'Saving', 
        'Dt:18':'Misc', 
        'TRF TO FD no. 004713024574':'Saving', 
        'DCardfee2429OCT16-SEP17ST119.8':'Misc', 
        'DECS DR':'Loan', 
        'ECSRTNCHGS290616CHG350+ST52.50':'Misc', 
        'TRF TO FD no. 004713024940':'Saving', 
        'Dt:19':'Misc', 
        'INF':2, 
        'Dt:27':'Misc', 
        'To RD Ac no 004725028466':'Saving', 
        'NFS':'Cash', 
        'IPS':1, 
        'VWL':2, 
        'MMT':'Misc', 
        'BIL':2, 
        'VPS':1, 
        'Dt:22':'Misc', 
        'ECS':'Loan', 
        'Dt:10':'Misc'}

    resultL = []
    detailCol = 3
    with open(inputFile) as fh:
         csvR = csv.reader(fh)
         headerRow = next(csvR)
         headerRow.append('CATEGORY')
         resultL.append(headerRow)
         for row in csvR:
             #print(row)
             categoryHeading = row[detailCol].split('/')[0]
             
             if not str(categoryListing[categoryHeading]).isdigit():
                category = categoryListing[categoryHeading]
             else:
                category = row[detailCol].split('/')[categoryListing[categoryHeading]]
             
             row.append(category)
             resultL.append(row)
             #print(category)
    return resultL

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

def analyze_csv(inputFile):
    resultL = []
    detailCol = 3
    amountCol = 4
    temp1 = set()
    catD = {}
    catmD = {}
    with open(inputFile) as fh:
         csvR = csv.reader(fh)
         headerRow = next(csvR)
         headerRow.append('CATEGORY')
         resultL.append(headerRow)
         for row in csvR:
             log.info(row[detailCol])
             cat1 = row[detailCol].split('/')[0]
             temp1.add(cat1)
             if cat1 not in catD:
                catD[cat1] = set()
                catmD[cat1] = 0
             catD[cat1].add(len(row[detailCol].split('/')))
             catmD[cat1] += float(row[amountCol])
             
                 
    log.info(temp1)
    for key, value in sorted(catD.items()):
        print('{},{},'.format(key, value))         

    for (value, key) in sorted([(value, key) for key, value in catmD.items()]):
        print('{},{},'.format(key, value))         

#analyze_csv(inputFile)

set_logging()
withCategory = extract_category(inputFile)
if withCategory:
   write_to_csv('output/expense_catg.csv', withCategory)

