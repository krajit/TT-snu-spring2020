#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 02:24:33 2019

@author: ajit
"""


slots = [
        '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00',
         '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
         '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', 
         '18:00', '18:30', '19:00', '19:30','20:00'
         ]


# read room inventory
import xlrd
rooms = dict()
roomFile = "RoomNumbers.xlsx"
wb = xlrd.open_workbook(roomFile) 
sheet = wb.sheet_by_index(0) # get first sheet
for i in range(1,sheet.nrows):
    r = sheet.cell_value(i,0)
    rooms[r] = dict()
    rooms[r]['capacity'] = int(sheet.cell_value(i,1))
    
    if int(sheet.cell_value(i,2)) == 1:
        rooms[r]['isBiometric'] = True
    else:
        rooms[r]['isBiometric'] = False
    
    rooms[r]['slots'] = dict()    
    days = ['M', 'T', 'W', 'Th', 'F','S','Sun']
    for d in days:
        rooms[r]['slots'][d] = dict()
        for s in slots:
            rooms[r]['slots'][d][s] = 'available'
            
sDayName = { 'MON': 'M', 'TUES': 'T', 'WED': 'W', 'THURS': 'Th', 'FRI':'F', 'SAT':'S', 'SUN':'Su'}
        


import re

def timeDictToTimeSet(lT):
    tSet = set()
    for d in lT:
        for t in lT[d]:
            tSet.add((d,t))
    return(tSet)


def timingsToSlots(timings):
    days = re.findall('[A-Z][a-z]*',timings.split(' ')[0])
    times = timings.split(' ')[1]
    tBegin = times.split('-')[0]
    tEnd = times.split('-')[-1]
    
    tBeginIndex = slots.index(tBegin)
    tEndIndex = slots.index(tEnd)
    cSlots = slots[tBeginIndex:tEndIndex]
    timeDict = dict()
    for d in days:
        timeDict[d] = cSlots
    return(timeDict)
    

courseToBeSkipped = {'ARC101', 'ARC317'}
specialRoomCourses = {
        'PHY105L1' : 'B116',
        'PHY105T1' : 'B116',
        'PHY563L1' : 'B116',
        'PHY563T1' : 'B116',
        'COM192L1' : 'B004',
        'COM192T1' : 'B004',
        'COM197L1' : 'B004',
        }
# read BMS course sheet
courses = dict()
roomFile = "S_TIME_TABLE_DUMP.xlsx"
wb = xlrd.open_workbook(roomFile) 
sheet = wb.sheet_by_index(0) # get first sheet
# fill in the rooms booking
for i in range(2,sheet.nrows):
    
    if sheet.cell_value(i,0) in courseToBeSkipped:
        continue
    
#    if 'ART' in sheet.cell_value(i,0): # skip art courses
#        continue
    
    if sheet.cell_value(i,0) in specialRoomCourses:
        continue
    
    cCode = sheet.cell_value(i,0)+sheet.cell_value(i,2)
    
    # don't worry about un announced courses
    if 'TBA' in sheet.cell_value(i,3):
        continue
    
    if 'P' in sheet.cell_value(i,2):
        continue
    
    day = sheet.cell_value(i,5)
    if day not in sDayName:
        continue
    
    if cCode not in courses:
        courses[cCode] = dict()
        
    
    if 'timings' not in courses[cCode]:     
        courses[cCode]['timings'] = dict()
        courses[cCode]['capacity'] = int(sheet.cell_value(i,14))
    
    tBegin = str(sheet.cell_value(i,3)).split('.')
    tBegin = str(int(tBegin[0]))+':'+tBegin[1]
    
    tEnd = str(sheet.cell_value(i,4)).split('.')
    
    #reformat
    if tEnd[1] == '55':
        tEnd[1] = '00'
        tEnd[0] = str(int(tEnd[0])+1)
    if tEnd[1] == '25':
        tEnd[1] = '30'
    tEnd[0] = str(int(tEnd[0]))

    tEnd = tEnd[0]+':'+tEnd[1]
    tBeginIndex = slots.index(tBegin)
    tEndIndex = slots.index(tEnd)
    
    
    cSlots = slots[tBeginIndex:tEndIndex]
    courses[cCode]['timings'][sDayName[day]] = cSlots

    if cCode[6] == 'T':
        #expandTut Slot to check consecutive
        tBeginM1 = max(tBeginIndex-1,0)
        tEndP1 = min(tEndIndex+1,len(slots))
        courses[cCode]['expandedTimings'] = dict()
        cSlots = slots[tBeginM1:tEndP1]
        courses[cCode]['expandedTimings'][sDayName[day]] = cSlots



# ERP list seem to be incomplete
# add non-uploaded timetable from google sheet data
# several courses seem to have wrong capacity entered in the erp
# download the schedule google sheet and update the course capacity
capacityFile = "SNU - Monsoon 2019.xlsx"
wb = xlrd.open_workbook(capacityFile) 
sheet = wb.sheet_by_index(0) # get first sheet
# fill in the rooms booking
capacityDict = dict()
for i in range(1,sheet.nrows):
    
    if 'PRAC' in sheet.cell_value(i,1):
        continue
    
    cCode = sheet.cell_value(i,0)
    if 'LEC' in sheet.cell_value(i,1):
        capacity = int(sheet.cell_value(i,6))
        capacityDict[cCode+'L'+sheet.cell_value(i,1)[-1]] = capacity
        
    if 'LEC' in sheet.cell_value(i,1):
        cCode = sheet.cell_value(i,0)+'L'+sheet.cell_value(i,1)[-1]
        
    if 'TUT' in sheet.cell_value(i,1):
        if len(sheet.cell_value(i,1)) == 4:
            cCode = sheet.cell_value(i,0)+'T'+sheet.cell_value(i,1)[-1]
        else:
            cCode = sheet.cell_value(i,0)+'T'+sheet.cell_value(i,1)[-2:]
            
        

# replace ERP capacity with google sheet copacity
for cCode in courses:
    if cCode in capacityDict:
        courses[cCode]['capacity'] = capacityDict[cCode]

    
for c in courses:
    if 'consecutiveTutorial' in courses[c]:
        print(c)

        
        





# identify courses with consecutive lectures and tutorials
for cCode in courses:
    # only look for tutorials with only one tutorial section
    if cCode[6] == 'T' and ((cCode[0:7]+str(2)) in courses):
        continue
    # only work on tutorial
    if cCode[6] != 'T':
        continue
    tExpandedTimeSet = timeDictToTimeSet(courses[cCode]['expandedTimings'])
    lTimeSet = timeDictToTimeSet(courses[cCode[0:6]+'L1']['timings'])
    if tExpandedTimeSet.intersection(lTimeSet):
        #simply expand lecture time slot of these courses
        courses[cCode[0:6]+'L1']['consecutiveTutorial'] = True
        courses[cCode[0:6]+'L1']['tutorialTimings'] = courses[cCode]['timings']
        courses[cCode]['consecutiveLectures'] = True
            

departments = {'ADP','BDA','BIO','CHY','MAT','PHY','ART','CCC','CED','CHD',
               'CSD','DES','DOM','ECO','EED','ENG','FAC','HIS','INT','ISM',
               'MEC','MED','MGT','MKT','OHM','SOC','STM'}    
        
bBlockPrefs = {'ADP','BDA','BIO','CHY','MAT','PHY'}
dBlockPrefs = departments.difference(bBlockPrefs)    
       
    
def findRoom(tSet,cCode,capacity, biometric = False):
    availableRoomSet = set()
    for r in rooms:
        if rooms[r]['capacity'] < capacity:
            continue
        if (biometric == True) and (rooms[r]['isBiometric'] == False):
            continue
        roomAvailable = True
        for ds in tSet:
            d,s = ds
            if 'available' not in rooms[r]['slots'][d][s]:
                roomAvailable = False
                continue
        if roomAvailable:
            availableRoomSet.add((r,rooms[r]['capacity']))
    
    if len(availableRoomSet) == 0:
        print(cCode, capacity, 'no room found')
        return 'TBA'

    # sort room 
    # increasing room capacity
    # and room preference
    if cCode[0:3] in bBlockPrefs:                    
        # sort room B block first
        availableRoomSet = sorted(sorted(availableRoomSet, key = lambda x : x[0], reverse = True), key = lambda x : x[1]) 
    else:
        # sort room D Block first
        availableRoomSet = sorted(sorted(availableRoomSet, key = lambda x : x[0], reverse = False), key = lambda x : x[1]) 
    return (availableRoomSet[0][0])    

# start booking the rooms
coursesList = sorted(courses.items(), key = lambda x: x[1]['capacity'], reverse=True)    
# make it dictionary again
courses = dict()
for c in coursesList:
    courses[c[0]] = c[1]
    
for cCode in courses:
    tSet = courses[cCode]['timings']
    tSet = timeDictToTimeSet(tSet)
    
    capacity = courses[cCode]['capacity']
    
    # biometric needed
    biometricNeeded = False
    if cCode[3] in '01':
        biometricNeeded = True

   # it cCode is  a tutorial and there is a consecutive lecture and tutorial 
    # skip because room is decided during finding rooms for lectures
    if 'consecutiveLectures' in courses[cCode]:
        continue

    
    # cCode is a lecture and there is a consecutive tutorial
    # just take the union of lecture and tutorial timeset     
    if 'consecutiveTutorial' in courses[cCode]:
        tSet = tSet.union(timeDictToTimeSet(courses[cCode]['tutorialTimings']))
        
    cRoom = findRoom(tSet,cCode,capacity,biometricNeeded)
    courses[cCode]['room'] = cRoom
    
    #reserve the room
    if 'TBA' not in cRoom:
        for d,s in tSet:
            rooms[cRoom]['slots'][d][s] = cCode
            
        # give room to consecutive tutorial
        if 'consecutiveTutorial' in courses[cCode]:
            tCode = cCode[0:-2]+'T1'
            courses[tCode]['room'] = cRoom
 
    

import xlsxwriter
workbook = xlsxwriter.Workbook('newRoomAssignments.xlsx') 
worksheet = workbook.add_worksheet()

capacityFile = "SNU - Monsoon 2019.xlsx"
wb = xlrd.open_workbook(capacityFile) 
sheet = wb.sheet_by_index(0) # get first sheet
# fill in the rooms booking

# header row
worksheet.write(0, 0, 'cCode')
worksheet.write(0, 1, 'LTP')
worksheet.write(0, 2, 'Time')
worksheet.write(0, 3, 'Instructor')
worksheet.write(0, 4, 'students')
worksheet.write(0, 5, 'room')
worksheet.write(0, 6, 'new room')

for i in range(1,sheet.nrows):
    for j in range(6):
        worksheet.write(i,j,sheet.cell_value(i,j))
    
    if 'LEC' in sheet.cell_value(i,1):
        cCode = sheet.cell_value(i,0)+'L'+sheet.cell_value(i,1)[-1]
        
    if 'TUT' in sheet.cell_value(i,1):
        if len(sheet.cell_value(i,1)) == 4:
            cCode = sheet.cell_value(i,0)+'T'+sheet.cell_value(i,1)[-1]
        else:
            cCode = sheet.cell_value(i,0)+'T'+sheet.cell_value(i,1)[-2:]
    
    if cCode in courses:
            worksheet.write(i,6,courses[cCode]['room'])
    elif cCode in specialRoomCourses:
        worksheet.write(i,6,specialRoomCourses[cCode])
    else:
        worksheet.write(i,6,'TBA')
        print(cCode, 'unknown error')
        
    if 'PRAC' in sheet.cell_value(i,1):
        worksheet.write(i,6,sheet.cell_value(i,5))
    
workbook.close()





for c in courses:
    if 'consecutiveTutorial' in courses[c]:
        print(c)
    




