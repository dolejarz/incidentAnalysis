from __future__ import division
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('seaborn-whitegrid')

#[DVP N, DVP S] ALWAYS

def getFileNames(rootdir,fileType):
    if (fileType == 'Time'):
        filt = 'DVP'
    elif (fileType == 'Incident'):
        filt = 'Segment'
    fileList = []
    for subdir, dirs, files in os.walk(rootdir): 
        temp = [] 
        for file in files:  
            if (filt in os.path.splitext(file)[0]): 
                temp.append(os.path.join(subdir, file)) 
        fileList.append(temp) 
    fileList = filter(lambda x: x != [], fileList)
    return fileList


def getCombinedDataFrames(fileList):
    '''
    returns a single dataframe for each folder
    '''
    dfList = []
    for folder in fileList:
        temp = pd.read_csv(folder[0])
        for i in range (1,len(folder)):
            temp.MinMeasuredTime += pd.read_csv(folder[i]).MinMeasuredTime
            temp.MaxMeasuredTime += pd.read_csv(folder[i]).MaxMeasuredTime
            temp.AvgMeasuredTime += pd.read_csv(folder[i]).AvgMeasuredTime
            temp.MedianMeasuredTime += pd.read_csv(folder[i]).MedianMeasuredTime 
        temp.Timestamp = pd.to_datetime(temp.Timestamp)
        dfList.append(temp)
    return dfList

def getSegmentDataFrames(fileList):
    '''
    returns a dataframe for each csv in the 2D fileList
    '''
    dfList = []
    for folder in fileList:
        temp = []
        for item in folder:
            temp.append(pd.read_csv(item))
        dfList.append(temp)
    return dfList
    
def selectDateIncident(day, data, direction):
    '''
    Returns list of incident data dataframes for inputed date on inputted segment in form [selected direction, other direction]
    '''
    data.StartDateTime = pd.to_datetime(data.StartDateTime)
    startDay = pd.to_datetime('2015-05-'+str(day)+' 00:00:00')
    if day == 31:
        endDay = pd.to_datetime('2015-06-'+str(1)+' 00:00:00')
    else:
        endDay = pd.to_datetime('2015-05-'+str(day+1)+' 00:00:00')
    return [data[(data.StartDateTime >= startDay) & (data.StartDateTime < endDay) & (data.EventDirection == direction)],data[(data.StartDateTime >= startDay) & (data.StartDateTime < endDay) & (data.EventDirection != direction)]]

def selectDateTravel(day, data):
    '''
    Returns bluetooth travel time data for inputed date on inputted segment
    '''
    data.Timestamp = pd.to_datetime(data.Timestamp)
    startDay = pd.to_datetime('2015-05-'+str(day)+' 00:00:00')
    if day == 31:
        endDay = pd.to_datetime('2015-06-'+str(1)+' 00:00:00')
    else:
        endDay = pd.to_datetime('2015-05-'+str(day+1)+' 00:00:00')
    return data[(data.Timestamp >= startDay) & (data.Timestamp < endDay)] 
    
def plotDate(day, incData, travelData, direction):
    '''
    Single line, input must be total travel time
    '''
    dayData = selectDateIncident(day, incData, direction)
    timeData = selectDateTravel(day, travelData)
    plt.figure(figsize=(16,12))
    plt.plot(timeData.Timestamp, timeData.AvgMeasuredTime/60,'b')
    for inc in dayData[0].StartDateTime:
        plt.axvline(x=inc,color='r',linewidth=1)
    for inc in dayData[-1].StartDateTime:
        plt.axvline(x=inc,color='k',linewidth=0.2)
    plt.title(str(day) + ' May 2015 - ' + str(direction))
    return   

def plotDateSegments(day, incData, travelData, direction, colors):
    '''
    Stacked area
    '''
    segmentTimes = []
    for segment in travelData:
        segmentTimes.append(selectDateTravel(day,segment))
    #TRAVEL TIME PLOT
    tempTimes = segmentTimes[0]
    plt.figure(figsize=(16,12),dpi=300)
    plt.ylim(0,60)
    plt.plot(tempTimes.Timestamp, tempTimes.AvgMeasuredTime/60,'k')
    plt.fill_between(tempTimes.Timestamp.as_matrix(),tempTimes.AvgMeasuredTime.as_matrix()/60,color=colors[0])
    for i in range(1,len(segmentTimes)):
        tempTimesFill = tempTimes.copy() 
        tempTimes.AvgMeasuredTime += segmentTimes[i].AvgMeasuredTime
        plt.plot(tempTimes.Timestamp, tempTimes.AvgMeasuredTime/60,'k')
        plt.fill_between(tempTimes.Timestamp.as_matrix(),tempTimesFill.AvgMeasuredTime.as_matrix()/60,tempTimes.AvgMeasuredTime.as_matrix()/60,color=colors[i])
    #INCIDENT PLOT  
    for i in range(len(incData)):
        #i = incData.index(segment)    
        dayData = selectDateIncident(day, incData[i], direction)
        for inc in dayData[0].StartDateTime:
            plt.axvline(x=inc,color=colors[i],linewidth=1.5)
        for inc in dayData[-1].StartDateTime:
            plt.axvline(x=inc,color=colors[i] ,linestyle='dashed',linewidth=0.2)
    #plt.title(str(day) + ' May 2015 - ' + str(direction))
    plt.savefig(str(direction) + '-' + str(day) + ' May 2015 - ' + '.png',format='png')
    return
    
def plotDateSegmentsSeperate(day, incData, travelData, direction, colors):
    '''
    multiple lines
    '''
    segmentTimes = []
    for segment in travelData:
        segmentTimes.append(selectDateTravel(day,segment))
    #TRAVEL TIME PLOT
    plt.figure(figsize=(16,12),dpi=300)
    plt.ylim(0,30)
    for i in range(len(segmentTimes)):
        plt.plot(segmentTimes[i].Timestamp, segmentTimes[i].AvgMeasuredTime/60, color=colors[i],linewidth=2)
    #INCIDENT PLOT  
    for i in range(len(incData)):  
        dayData = selectDateIncident(day, incData[i], direction)
        for inc in dayData[0].StartDateTime:
            plt.axvline(x=inc,color=colors[i],linewidth=1.5)
        for inc in dayData[-1].StartDateTime:
            plt.axvline(x=inc,color=colors[i] ,linestyle='dashed',linewidth=0.2)
    plt.title(str(day) + ' May 2015 - ' + str(direction))
    #plt.savefig(str(direction) + '-' + str(day) + ' May 2015 - ' + '.png',format='png')
    return
   
def costReturn(rate, vol, t, slowIn, fastIn):
    integral = np.trapz(y=slowIn.AvgMeasuredTime.as_matrix(),x=t.as_matrix()) - np.trapz(y=fastIn.AvgMeasuredTime.as_matrix(),x=t.as_matrix())
    delay = int(integral)/3600000000000
    cost = int(delay*rate*vol)
    return cost

def normalCombined(days, travelData):
    '''
    input = list of normal days, combined travel time 
    output = series of mean of normal days
    '''

    dayTimes = selectDateTravel(days[0],travelData).AvgMeasuredTime
    for day in days[1:]:
        dayTimes = pd.concat([dayTimes.reset_index(drop=True),selectDateTravel(day,travelData).AvgMeasuredTime.reset_index(drop=True)],ignore_index=True,axis=1) # THIS SHIT IS NOT WORKING WTFFFFF
    return dayTimes.mean(axis=1)
    
    
    
#2016 04 07 Complete_Dataset_Final_Copy_v8.00
print('Running...')
#colors = ['b','g','c','m','y']
colors = ['#e6e6e6','#b3b3b3','#808080','#4d4d4d','#1a1a1a']
#rawData = pd.read_csv('IncidentData.csv',low_memory=False)
#cleanData = pd.concat([rawData.ID,rawData.EventLocation,rawData.EventDirection,rawData.ShiftReportName,rawData.original_incident_reason,rawData.I_Lattitude,rawData.I_Longitude,rawData.StartDate,rawData.StartTime,rawData.StartDateTime,rawData.EndDate,rawData.EndTime,rawData.EndDateTime],axis=1) 
#cleanData = cleanData[cleanData.EventLocation == 'DVP']
#cleanData.StartDateTime = pd.to_datetime(cleanData.StartDateTime)
nNormal = [5,6,11,22,25]
sNormal = [4,8,11,14,22]
    
rootdir = 'C:\Users\dolejar\Documents\Incident Analysis\All of may'
timeFileList = getFileNames(rootdir,'Time')
incidentFileList = getFileNames(rootdir, 'Incident')

combinedTimes = getCombinedDataFrames(timeFileList)
segmentTimes = getSegmentDataFrames(timeFileList)

segmentIncidents = getSegmentDataFrames(incidentFileList)

weatherData = pd.read_csv('TO-weather-01012015-12312015.csv')
weatherData.Date = pd.to_datetime(weatherData.Date)

#plotDate(16,cleanData,combinedTimes[1],'SB')
plotDateSegmentsSeperate(28,segmentIncidents[0],segmentTimes[1],'SB',colors)
plotDateSegments(28,segmentIncidents[0],segmentTimes[1],'SB',colors)

test = normalCombined(sNormal,combinedTimes[1])

#for i in range(1,31):
#    print(i)
#    plotDateSegments(i,segmentIncidents[0],segmentTimes[1],'SB',colors)
#    plotDateSegments(i,segmentIncidents[0],segmentTimes[0],'NB',colors)
    





