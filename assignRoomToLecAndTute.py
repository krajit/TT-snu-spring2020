#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 00:32:41 2019

@author: ajit
"""

# import slots and courses list from COS2FET
import pickle
coursesPickle = open('courses.pickle','rb')
courses = pickle.load(coursesPickle) 

# deflate instructor from CCC608
courses['CCC608']['lecSections']['LEC1']['instructors'] = courses['CCC608']['lecSections']['LEC1']['instructors'][0:1]

# copy CCC608 ids to all other CCC
for c in courses['CCC608']['overlapsWith']:
    courses[c]['lecSections']['LEC1']['ids'] = courses['CCC608']['lecSections']['LEC1']['ids']
    
slotsPickle = open('slots.pickle','rb')
slots = pickle.load(slotsPickle)
#
#
#


##----------------------------------------
#read exported csv format of the latest timetable
import csv
with open('csv/snu-timetable/snu-timetable_timetable.csv', 'r') as ff:
  reader = csv.reader(ff)
  activities = list(reader)
 
activitiesTime = dict()  
  
for a in activities:
    if a[0] not in activitiesTime:
        activitiesTime[a[0]] = dict()
        activitiesTime[a[0]][a[1]] = []
        activitiesTime[a[0]][a[1]].append(a[2])
    elif a[1] not in activitiesTime[a[0]]:
        activitiesTime[a[0]][a[1]] = []
        activitiesTime[a[0]][a[1]].append(a[2])
    else:
        activitiesTime[a[0]][a[1]].append(a[2])



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
    days = ['M', 'T', 'W', 'Th', 'F']
    for d in days:
        rooms[r]['slots'][d] = dict()
        for s in slots:
            rooms[r]['slots'][d][s] = 'available'
    
#temporarily make D217 biometric
rooms['D217']['isBiometric'] = True

# set lecture capacity for each lecture sections
for c in courses:
    if 'lecSections' in courses[c]:
        courses[c]['lecCapacity'] = int(int(courses[c]['CourseCapacity'])/len(courses[c]['lecSections']))
    else:
        courses[c]['lecCapacity'] = courses[c]['CourseCapacity']
    
# sort according to capacity 
# gives list
coursesList = sorted(courses.items(), key = lambda x: x[1]['lecCapacity'], reverse=True)    
# make it dictionary again
courses = dict()
for c in coursesList:
    courses[c[0]] = c[1]

# sort rooms accorig to size
# gives list
roomsList = sorted(rooms.items(), key = lambda x: x[1]['capacity'], reverse=False)

# make it into dictionry again
rooms = dict()
for r in roomsList:
    rooms[r[0]] = r[1]

roomNotAssigned = []            

# start filling in rooms for each of the lecture sections
# start from the biggest lecures and fit it in the smallest possible room
def assignRooms(level = '1'):
    for ci in courses:
        c = courses[ci]
        biometricRoomNeeded = False
        if (ci[3] == '1' or ci[3] == '0'):
            biometricRoomNeeded = True
            
        if ci[3] not in level:
            continue
        
        if 'lecSections' in c:
            for li in c['lecSections']:
                lecTimes = {}
                l = c['lecSections'][li]
                
                if 'ids' not in l:
                    print('looks like', ci, 'has been removed from the FET data')
                    continue
                lecIds = l['ids']
                
                for i in lecIds:
                    if str(i) not in activitiesTime:
                        print('looks like', ci, 'has been removed from the FET data')
                        continue
                    x = activitiesTime[str(i)]
                    for t in x:
                        lecTimes[t] = x[t]
                courses[ci]['lecSections'][li]['timings'] = lecTimes 
                # lecTimes is a dictionary holding information for all the times this lecture is happening
                # find the smallest rooms that fits this lecture capacity and is available
                lecCapacity = c['lecCapacity']
                # pretend that lecCapacity for MAT103 is 300
                if (lecCapacity > 300):
                    lecCapacity = 300
                lecRoom = 'no room'
                roomAssigned = False
                for r in rooms:
                    if biometricRoomNeeded and (not rooms[r]['isBiometric']):
                        continue
                    if not roomAssigned:
                        roomCapacity = rooms[r]['capacity']
                        # check for room capacity
                        if (lecCapacity <= roomCapacity):
                            # check if available
                            isRoomAvailable = True
                            for d in lecTimes: # loop over lec days 
                                for s in lecTimes[d]: # loop over lec times
                                    if (rooms[r]['slots'][d][s] != 'available'):
                                        isRoomAvailable = False
                            # take the room if available
                            if isRoomAvailable:
                                lecRoom = r
                                courses[ci]['lecSections'][li]['room'] = lecRoom
                                roomAssigned = True
                                # mark non availability this room in these slots
                                for d in lecTimes: # loop over lec days 
                                    for s in lecTimes[d]: # loop over lec times
                                        rooms[r]['slots'][d][s] = ci+'L'
                if not roomAssigned:
                    print(ci,courses[ci]['lecCapacity'] ,'lec, room not found')
                    roomNotAssigned.append(ci)
    
    
        if 'tutSections' in c:
            for li in c['tutSections']:
                lecTimes = {}
                l = c['tutSections'][li]
                lecIds = l['ids']
                for i in lecIds:
                                        
                    if str(i) not in activitiesTime:
                        print('looks like', ci, 'has been removed from the FET data')
                        continue

                    x = activitiesTime[str(i)]
                    for t in x:
                        lecTimes[t] = x[t]
                courses[ci]['tutSections'][li]['timings'] = lecTimes
                # lecTimes is a dictionary holding information for all the times this lecture is happening
                # find the smallest rooms that fits this lecture capacity and is available
                lecCapacity = c['lecCapacity']
                # pretend that lecCapacity for MAT103 is 300
                lecCapacity = min(30, lecCapacity)
                lecRoom = 'no room'
                roomAssigned = False
                for r in rooms:
                    if biometricRoomNeeded and (not rooms[r]['isBiometric']):
                        continue
                    if not roomAssigned:
                        roomCapacity = rooms[r]['capacity']
                        # check for room capacity
                        if (lecCapacity <= roomCapacity):
                            # check if available
                            isRoomAvailable = True
                            for d in lecTimes: # loop over lec days 
                                for s in lecTimes[d]: # loop over lec times
                                    if (rooms[r]['slots'][d][s] != 'available'):
                                        isRoomAvailable = False
                            # take the room if available
                            if isRoomAvailable:
                                lecRoom = r
                                courses[ci]['tutSections'][li]['room'] = lecRoom
                                roomAssigned = True
                                # mark non availability this room in these slots
                                for d in lecTimes: # loop over lec days 
                                    for s in lecTimes[d]: # loop over lec times
                                        rooms[r]['slots'][d][s] = ci+'T'
                if not roomAssigned:
                    print(ci, 'tute, room not found')
                                        
                            
        if 'labSections' in c:
            for li in c['labSections']:
                lecTimes = {}
                l = c['labSections'][li]
                
                if 'ids' not in l: # ignore project courses
                    continue
                
                lecIds = l['ids']
                for i in lecIds:
                    x = activitiesTime[str(i)]
                    for t in x:
                        lecTimes[t] = x[t]
                courses[ci]['labSections'][li]['timings'] = lecTimes
                
# assign rooms to  first year coures first to biometric rooms
assignRooms(level = '01')

# then assign higher level coureses to any rooms
assignRooms(level = '23456789')

##----------------------
print('\n....')
print('Some rooms have not been assigned rooms. For these course, different days are getting mapped to different rooms...')
for ci in roomNotAssigned:
    lectureSlots = courses[ci]['lecSections']['LEC1']['timings']
    courses[ci]['lecSections']['LEC1']['room'] = ''
    
    for dayi in lectureSlots:
        dayiSlots = lectureSlots[dayi]
        roomAssigned = False
        
        for r in rooms:
            # skip is room is not big enough
            if rooms[r]['capacity'] < courses[ci]['lecCapacity']:
                continue
            
            isRoomAvailable = True
            for s in dayiSlots:
                if (rooms[r]['slots'][dayi][s] != 'available'):
                    isRoomAvailable = False
                    
            if isRoomAvailable:
                # make the room unavailalbe
                for s in dayiSlots:
                    rooms[r]['slots'][dayi][s] = ci
                
                # note down the room for the lecture
                courses[ci]['lecSections']['LEC1']['room'] = courses[ci]['lecSections']['LEC1']['room'] + dayi+"("+r+")"
                roomAssigned = True
                
            if roomAssigned:
                break
        if  not roomAssigned:
            print(ci,dayi, dayiSlots,'rooms not found')
            courses[ci]['lecSections']['LEC1']['room'] = 'TBA'


##---------------------

# lets write down the time table in excel
def formatTime(slotsList):
    lastSlot = slotsList[-1]
    bhh= slotsList[0][0:2]
    bhh = str(int(bhh))
    bmm = slotsList[0][-2:]
    ehh= slotsList[-1][0:2]
    ehh = str(int(ehh))
    emm = slotsList[-1][-2:]
    if emm == '00':
        emm = '30'
    elif (emm == '30'):
        emm = '00'
        ehh=str(int(ehh)+1)
    return bhh+':'+bmm+'-'+ehh+':'+emm
        

def cleanInstructor(ins):
    x = ins.split('[')
    return x[0]
        
# record popular choices
# import xlsxwriter module 
import xlsxwriter 
workbook = xlsxwriter.Workbook('new-timeTable-SNU-Fall2019.xlsx') 
worksheet = workbook.add_worksheet()

row = 0
codeCol = 0
meetingType = 1 # lec,tut,prac
timeCol = 2
instructorCol = 3
studentCol = 4
roomCol = 5

# header row
worksheet.write(row, codeCol, 'cCode')
worksheet.write(row, meetingType, 'LTP')
worksheet.write(row, timeCol, 'Time')
worksheet.write(row, instructorCol, 'Instructor')
worksheet.write(row, studentCol, 'Students')
worksheet.write(row, roomCol, 'Room')
row = row+1

def sortedDays(times, cCode):
    
    # sort days
    x = dict()
    
    if 'M' in times:
        x['M'] = times['M']
    if 'T' in times:
        x['T'] = times['T']
    if 'W' in times:
        x['W'] = times['W']
    if 'Th' in times:
        x['Th'] = times['Th']
    if 'F' in times:
        x['F'] = times['F']
    
    days = list(x)
    D = ''
    hh = formatTime( times[days[0]])
    
    for d in days:
        if (times[d] != times[days[0]]):
            print(cCode, 'error', times)
            return(str(x))
        D = D+d
    
    x = D+' '+hh
    return(x)
        


    
for ci in courses:
    c = courses[ci]
    if 'lecSections' in c:
        for li in c['lecSections']:
            if 'timings' in c['lecSections'][li]:
                if len(c['lecSections'][li]['timings']) == 0:
                    continue
                time = sortedDays(c['lecSections'][li]['timings'],ci)                
                room = ''
                if 'room' in c['lecSections'][li]:
                    room = c['lecSections'][li]['room']
                else:
                    room = 'TBA'
                
                instructor = ''
                for i in c['lecSections'][li]['instructors']:
                    instructor = instructor+cleanInstructor(i)+','
                instructor = instructor[0:-1]
                
                studentSet = ''
                for s in c['lecSections'][li]['students']:
                    studentSet = studentSet+s+','
                studentSet = studentSet[0:-1]
                
                worksheet.write(row, codeCol, ci)
                worksheet.write(row, meetingType, li)
                worksheet.write(row, timeCol, time)
                worksheet.write(row, instructorCol, instructor)
                worksheet.write(row, studentCol, studentSet)
                worksheet.write(row, roomCol, room)
                
                row = row+1
                
    if 'tutSections' in c:
        for li in c['tutSections']:
            if 'timings' in c['tutSections'][li]:
                if len(c['tutSections'][li]['timings']) == 0:
                    continue

                time = sortedDays(c['tutSections'][li]['timings'],ci)
                
                if 'room' not in c['tutSections'][li]:
                    c['tutSections'][li]['room'] = 'TBA'
                    
                room = c['tutSections'][li]['room']
                instructor = ''
                for i in c['tutSections'][li]['instructors']:
                    instructor = instructor+cleanInstructor(i)+','
                instructor = instructor[0:-1]
                
                studentSet = ''
                for s in c['tutSections'][li]['students']:
                    studentSet = studentSet+s+','
                studentSet = studentSet[0:-1]
                
                worksheet.write(row, codeCol, ci)
                worksheet.write(row, meetingType, li)
                worksheet.write(row, timeCol, time)
                worksheet.write(row, instructorCol, instructor)
                worksheet.write(row, studentCol, studentSet)
                worksheet.write(row, roomCol, room)
                
                row = row+1
                
    if 'labSections' in c:
        for li in c['labSections']:
            if 'timings' in c['labSections'][li]:
                time = sortedDays(c['labSections'][li]['timings'],ci)
                
                room = c['labSections'][li]['room']
                instructor = ''
                for i in c['labSections'][li]['instructors']:
                    instructor = instructor+cleanInstructor(i)+','
                instructor = instructor[0:-1]
                
                studentSet = ''
                for s in c['labSections'][li]['students']:
                    studentSet = studentSet+s+','
                studentSet = studentSet[0:-1]
                
                worksheet.write(row, codeCol, ci)
                worksheet.write(row, meetingType, li)
                worksheet.write(row, timeCol, time)
                worksheet.write(row, instructorCol, instructor)
                worksheet.write(row, studentCol, studentSet)
                worksheet.write(row, roomCol, room)
                
                row = row+1
workbook.close()                         
                    
                
            

 



