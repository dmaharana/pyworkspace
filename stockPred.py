import csv
from sklearn import linear_model
#import numpy as np
'''
1. copy the 'Adj Close' col from the csv
2. Reverse the order - source is in decending order
3. create two list - 
	 - P(t) l1
	 - P(t-1) & P(t-2) l2
4. split the l1 & l2 into taining 75% and testing 25% lists (4)
5. build the model with training data
6. use the model on testing data to get the accuracy of the model
'''


def get_data(inputfile, indexOfTarget):
    MAXRECS = 80
    count = 0
    
    targetL = []
    
    with open(inputfile) as fh:
         csvReader = csv.reader(fh)
         next(csvReader)
         for row in csvReader:
             count += 1
             if count <= MAXRECS:
                targetL.append(float(row[indexOfTarget]))
             else:
                break

    return targetL

def reverse_list(inputL):
    resultL = []
    for item in inputL:
        resultL.insert(0,item)
    return resultL
    
def return_attributes(targetL):
    #t-1 & t-2
    resultL = []
    #for i, price in enumerate(targetL):
    for i in range(2, len(targetL)):
        t_minus_1 = targetL[i-1]
        t_minus_2 = targetL[i-2]
        resultL.append([t_minus_1, t_minus_2])
        #print ('index = {}, t_minus_1 = {}, t_minus_2 = {}'.format(i, t_minus_1, t_minus_2))
    return resultL
        
def generate_training_testing_data(inputL):
    #testing data is 25% of total data
    splitIndex = int(len(inputL)/4)
    trainingL = inputL[:-splitIndex]
    testingL = inputL[-splitIndex:]
    
    return(trainingL, testingL)
    
def build_ml_model(trainingAttribute, trainingTarget):
    #print ('Attributes----------\n', trainingAttribute, len(trainingAttribute), type(trainingAttribute))
    #print ('Target-----------\n',trainingTarget, len(trainingTarget), type(trainingTarget))
    
    ml_model = linear_model.LinearRegression()
    ml_model.fit(trainingAttribute, trainingTarget)
    
    return ml_model
    
def main():
    myDataFile = '/home/nikki/Documents/sentimentAnalysis/webscrapping/output/TCS.NS.csv'
    targetIndex = 6
    
    adjClosePrice = get_data(myDataFile, targetIndex)
    #print ('adjClosePrice:',adjClosePrice)
    
    #target is close price
    acendingPrice = reverse_list(adjClosePrice)
    #print ('acendingPrice:',acendingPrice, len(acendingPrice))
    
    #ClosePrice(t-1) and ClosePrice(t-2) are the attributes
    attributes = return_attributes(acendingPrice) 
    #print ('attributes', attributes, len(attributes))
    
    #split into training and testing data sets
    (targetPriceTraining, targetPriceTesting) = generate_training_testing_data(acendingPrice[2:]) 
    #print (len(targetPriceTraining), len(targetPriceTesting))
    
    (attributeTraining, attributeTesting) = generate_training_testing_data(attributes) 
    #print (len(attributeTraining), len(attributeTesting))
    
    machineLearningModel = build_ml_model(attributeTraining, targetPriceTraining)
    
    predictionScore = machineLearningModel.score(attributeTesting, targetPriceTesting)
    print ('Prediction score: ', predictionScore)

main()


