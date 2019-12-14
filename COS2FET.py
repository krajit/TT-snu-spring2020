#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 17:00:47 2019

@author: ajit
"""

import re, csv
import random, xlrd
import pickle

# some preparotory instructions
print('\nWarning: File downloaded from COS contains Ziaur Rehman. It is a dummy instructor name. Make sure to replace it with unique name for each activity.\n')
print('\nWarning: Large courses with multiple tutorials generally have instructor names in the tutorials section. Make sure to replace that with course code + TAi to get accurate time table.\n')


#--------------------------------------------------------
# laod a starting template for .fet file readable by FET.
templatePath = 'basicTemplate.fet'
basicTemplate = open(templatePath,"r").read()
formattedData = basicTemplate 
fetFileName = 'snu-timetable_lab.fet'

# hours, written vertically aligned to easily comment out few slots
slots = ['08:00', '08:30', 
         '09:00', '09:30', '10:00', '10:30', '11:00',
         '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
         '15:00', '15:30', 
         '16:00', 
         '16:30', 
         '17:00', 
         '17:30', 
#         '18:00',
#         '18:30', 
#         '19:00', 
#         '19:30',
         ]

import studentsGroupXML as stuXML
studentGroups = stuXML.studentGroups
studentsListXML = stuXML.studentsListXML


# read course offering data
import readCOSdata as COS
courseList = COS.courseList # a dictionary containing details of each course read from COS excel file

# add students to complusory courses
# loop over courses and add the set of major studetns to it
        
print('Adding major students in their compulsory courses ......')

for ci in courseList:
    c = courseList[ci]    
    
    #only work with major courses in this loop
    if (c['CourseType'] != 'Major') :
            continue
        
    if 'lecSections' in c:
        for li in c['lecSections']:
            courseList[ci]['lecSections'][li]['students'] = courseList[ci]['lecSections'][li]['students'].union(
                    courseList[ci]['lecSections'][li]['potentialStudents']) 
            del courseList[ci]['lecSections'][li]['potentialStudents'] 
            
    if 'tutSections' in c:
        for li in c['tutSections']:
            courseList[ci]['tutSections'][li]['students'] = courseList[ci]['tutSections'][li]['students'].union(
                    courseList[ci]['tutSections'][li]['potentialStudents'])
            del courseList[ci]['tutSections'][li]['potentialStudents'] 

    if 'labSections' in c:
        for li in c['labSections']:
            courseList[ci]['labSections'][li]['students'] = courseList[ci]['labSections'][li]['students'].union(
                    courseList[ci]['labSections'][li]['potentialStudents']) 
            del courseList[ci]['labSections'][li]['potentialStudents'] 
        
            
# adding major elective courses
print('......')
print('Adding students in major electives ......')
print('......')

maxMajorElectives = 10
enrolledMajorElectives = dict()
for y in studentGroups:
    for s in studentGroups[y]:
        enrolledMajorElectives[s] = set() #maxMajorElectives

for ci in courseList:
    c = courseList[ci]
    # skip if not major electives type
    if (c['CourseType'] != 'Major Elective'):
        continue
    # get list of all students
    
    if ci == 'CED636':
        continue
    
    
    cStudents = set()
    for li in c['lecSections']:
        cStudents = cStudents.union(c['lecSections'][li]['potentialStudents'])


 
    for s in cStudents:
        # increase maxMajorElectives for all except CSE
        # overlap MAT494 with CSD311
#        if (s[0:3] != 'CSE'):
#            maxMajorElectives = 3
#            if (s[0:3] == 'MAT'):
#                maxMajorElectives = 3
#        else:
#            maxMajorElectives = 3
#        
        
        if len(enrolledMajorElectives[s]) >= maxMajorElectives: # dont enroll s in ci
            print('Student group', s, 'not added in ', ci, 'because too many major electives.\nManually add',
                      ci, 'in the same time as ',enrolledMajorElectives[s],'\n')

        else: # enroll s in ci
            # add course in students major electives courses
            enrolledMajorElectives[s].add(ci)            
            # add student in the course lecture, tut, practical
            if 'lecSections' in c:
                for li in c['lecSections']:
                    if s in c['lecSections'][li]['potentialStudents']:
                        c['lecSections'][li]['students'].add(s)
            if 'tutSections' in c:
                for li in c['tutSections']:
                    if s in c['tutSections'][li]['potentialStudents']:
                        c['tutSections'][li]['students'].add(s)
            if 'labSections' in c:
                for li in c['labSections']:
                    if s in c['labSections'][li]['potentialStudents']:
                        c['labSections'][li]['students'].add(s)
        

## add year1, year2, year3 in on one randomly selected CCC
# Then manually make sure all CCC overlaps
#courseList['CCC510']['studentsSet'].add('year1')


anchorCCC = 'CCC608'

courseList[anchorCCC]['lecSections']['LEC1']['students'].add('year1')  
courseList[anchorCCC]['lecSections']['LEC1']['students'].add('year2')  
courseList[anchorCCC]['lecSections']['LEC1']['students'].add('year3')  
courseList[anchorCCC]['lecSections']['LEC1']['students'].add('year4')  

## add other CCC instructors in CCC515
## don't generate timetable for other CCC

courseList['CCC608']['overlapsWith'] = dict()
for ci in courseList:
    c = courseList[ci]
    
    if 'CCC' not in ci:
        continue
    
    if ci != anchorCCC:
        courseList[anchorCCC]['overlapsWith'][ci] = c['lecSections']['LEC1']['instructors']
        courseList[anchorCCC]['lecSections']['LEC1']['instructors'] = courseList[anchorCCC]['lecSections']['LEC1']['instructors'] + c['lecSections']['LEC1']['instructors']
    
                  
## map courses to activities
tutDurationSet = set()
activityTagSet= set()
activityString = "Students Sets,Subject,Teachers,Activity Tags,Total Duration,Split Duration,Min Days,Weight,Consecutive\n"

def splitLec(totalDuration, lecDuration = '2'):
    if (totalDuration == '2'):
        return '2'
    elif (totalDuration == '3'):
        return '3'
    elif (totalDuration == '4'):
        if (lecDuration == '4'):
            return '4'
        else:
            return '2+2'
    elif (totalDuration == '6'):
        if (lecDuration == '3'):
            return '3+3'
        else:
            return '2+2+2'
    elif (totalDuration == '8'):
        return '4+4'
    elif (totalDuration == '10'):
        return '5+5'
    else:
        return ''
      
        
activityListXML = '<Activities_List>\n'
activityId = 0
activityGroupId = 0
for cIndex, c in courseList.items():
    
    #among CCC only map CCC515
    if ('CCC' in cIndex) and (cIndex != anchorCCC):
        continue
    
    
    if 'lecSections' in c:
        for lIndex, l in c['lecSections'].items():
            activityXML = '<Activity>\n'
            activityXML = activityXML + '\t<Subject>'+cIndex+'</Subject>\n'
            for s in l['students']:
                activityXML = activityXML + '\t<Students>'+s+'</Students>\n'
            teachers = ''
            for i in l['instructors']:
                activityXML = activityXML + '\t<Teacher>'+i+'</Teacher>\n'
            activityTag = lIndex #'LEC+AnyRoom+'+lIndex
            activityTagSet.add(activityTag)
            activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'

            if cIndex[0:3] != "CCC":
                activityTagSet.add(cIndex[0:3])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:3]+'</Activity_Tag>\n'
                activityTagSet.add(cIndex[0:4])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:4]+'</Activity_Tag>\n'
            
            if (cIndex[0:3] == 'CCC'):
                activityTag = 'CCC'
                activityTagSet.add(activityTag)
                activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'

            for aTag in l['activityTags']:
                activityTagSet.add(aTag)
                activityXML = activityXML + '\t<Activity_Tag>'+aTag+'</Activity_Tag>\n'
                

            totalDuration = str(c['LectureHoursPerWeek'])
            if (int(totalDuration) >= 12):
                print(cIndex + " abnormally high lecture hours. Skipping")
                continue
            lecDuration = str(c['LectureDuration'])
            if (cIndex[0:3] == 'CCC'):
                lecDuration = '3'            
               
                
            activityTagSet.add('LecTTh')
            splitDuration = splitLec(totalDuration,lecDuration)
            if splitDuration == '3+3':
                activityXML = activityXML + '\t<Activity_Tag>LecTTh</Activity_Tag>\n'
            activityXML = activityXML + '\t<Duration>'+splitDuration[0]+'</Duration>\n'
            activityXML = activityXML + '\t<Total_Duration>'+totalDuration+'</Total_Duration>\n'
                
            # add an acitivtyID for each contact session
            # needed for forcing lectures on diff days to to on same time 
            activityIdSet = set()
            for i in range(0,len(splitDuration),2):
                activityId = activityId + 1
                activityIdSet.add(activityId)
                # get first lecture id in week
                if (i == 0):
                    activityGroupId = activityId
                activityXMLi = activityXML
                activityXMLi = activityXMLi + '\t<Id>'+str(activityId)+'</Id>\n'
                activityXMLi = activityXMLi + '\t<Activity_Group_Id>'+str(activityGroupId)+'</Activity_Group_Id>\n'
                activityXMLi = activityXMLi + '\t<Active>true</Active>\n'
                activityXMLi = activityXMLi + '\t<Comments></Comments>\n'
                activityXMLi = activityXMLi + '</Activity>\n'
                activityListXML = activityListXML + activityXMLi
            courseList[cIndex]['lecSections'][lIndex]['ids']=activityIdSet

    if 'tutSections' in c:
        for lIndex, l in c['tutSections'].items():
            activityXML = '<Activity>\n'
            activityXML = activityXML + '\t<Subject>'+cIndex+'</Subject>\n'
            for s in l['students']:
                activityXML = activityXML + '\t<Students>'+s+'</Students>\n'
            for i in l['instructors']:
                activityXML = activityXML + '\t<Teacher>'+i+'</Teacher>\n'
            activityTag = lIndex #'TUT+AnyRoom+'+lIndex
            activityTagSet.add(activityTag)
            
            for aTag in l['activityTags']:
                activityTagSet.add(aTag)
                activityXML = activityXML + '\t<Activity_Tag>'+aTag+'</Activity_Tag>\n'
#            activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'
            
            activityTagSet.add('tutorial')
            activityXML = activityXML + '\t<Activity_Tag>tutorial</Activity_Tag>\n'
            
            if cIndex[0:3] != "CCC":
                activityTagSet.add(cIndex[0:3])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:3]+'</Activity_Tag>\n'
                activityTagSet.add(cIndex[0:4])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:4]+'</Activity_Tag>\n'


            if (cIndex[0:3] == 'CCC'):
                activityTag = 'CCC'
                activityTagSet.add(activityTag)
                activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'
            
            totalDuration = str(c['TutorialHoursPerWeek'])
            if (int(totalDuration) >= 12):
                print(cIndex + " abnormally high tutorials hours. Skipping")
                continue
            splitDuration = totalDuration#splitLec(totalDuration,'3')
            activityXML = activityXML + '\t<Duration>'+splitDuration[0]+'</Duration>\n'
            activityXML = activityXML + '\t<Total_Duration>'+totalDuration+'</Total_Duration>\n'

            # add an acitivtyID for each contact session
            # needed for forcing lectures on diff days to to on same time 
            activityIdSet = set()
            for i in range(0,len(splitDuration),2):
                activityId = activityId + 1
                activityIdSet.add(activityId)
                # get first lecture id in week
                if (i == 0):
                    activityGroupId = activityId
                activityXMLi = activityXML
                activityXMLi = activityXMLi + '\t<Id>'+str(activityId)+'</Id>\n'
                activityXMLi = activityXMLi + '\t<Activity_Group_Id>'+str(activityGroupId)+'</Activity_Group_Id>\n'
                activityXMLi = activityXMLi + '\t<Active>true</Active>\n'
                activityXMLi = activityXMLi + '\t<Comments></Comments>\n'
                activityXMLi = activityXMLi + '</Activity>\n'
                activityListXML = activityListXML + activityXMLi
            courseList[cIndex]['tutSections'][lIndex]['ids']=activityIdSet
    if 'labSections' in c:
        for lIndex, l in c['labSections'].items():
            activityXML = '<Activity>\n'
            activityXML = activityXML + '\t<Subject>'+cIndex+'</Subject>\n'
            for s in l['students']:
                activityXML = activityXML + '\t<Students>'+s+'</Students>\n'
            for i in l['instructors']:
                activityXML = activityXML + '\t<Teacher>'+i+'</Teacher>\n'
            activityTag = l['room'][0:4] #'LAB' +'+'+ l['room'][0:4]+'+'+lIndex
            activityTagSet.add(activityTag)
            activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'
            
            
            for aTag in l['activityTags']:
                activityTagSet.add(aTag)
                activityXML = activityXML + '\t<Activity_Tag>'+aTag+'</Activity_Tag>\n'
            
            activityTagSet.add("Lab")
            activityXML = activityXML + '\t<Activity_Tag>'+"Lab"+'</Activity_Tag>\n'

            
            if cIndex[0:3] != "CCC":
                activityTagSet.add(cIndex[0:3])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:3]+'</Activity_Tag>\n'
                activityTagSet.add(cIndex[0:4])
                activityXML = activityXML + '\t<Activity_Tag>'+cIndex[0:4]+'</Activity_Tag>\n'


            if (cIndex[0:3] == 'CCC'):
                activityTag = 'CCC'
                activityTagSet.add(activityTag)
                activityXML = activityXML + '\t<Activity_Tag>'+activityTag+'</Activity_Tag>\n'
            
            totalDuration = str(c['PracticalHoursPerWeek'])
            if (int(totalDuration) >= 12):
                print(cIndex + " abnormally high practical hours. Skipping")
                continue
            splitDuration = totalDuration # no splitting of lab hours
            if cIndex == 'CHD319': # split lab
                splitDuration = '4+4'                
            activityXML = activityXML + '\t<Duration>'+splitDuration[0]+'</Duration>\n'
            activityXML = activityXML + '\t<Total_Duration>'+totalDuration+'</Total_Duration>\n'
            # add an acitivtyID for each contact session
            # needed for forcing lectures on diff days to to on same time 
            activityIdSet = set()
            for i in range(0,len(splitDuration),2):
                activityId = activityId + 1
                activityIdSet.add(activityId)
                # get first lecture id in week
                if (i == 0):
                    activityGroupId = activityId
                activityXMLi = activityXML
                activityXMLi = activityXMLi + '\t<Id>'+str(activityId)+'</Id>\n'
                activityXMLi = activityXMLi + '\t<Activity_Group_Id>'+str(activityGroupId)+'</Activity_Group_Id>\n'
                activityXMLi = activityXMLi + '\t<Active>true</Active>\n'
                activityXMLi = activityXMLi + '\t<Comments></Comments>\n'
                activityXMLi = activityXMLi + '</Activity>\n'
                activityListXML = activityListXML + activityXMLi
            courseList[cIndex]['labSections'][lIndex]['ids']=activityIdSet


# Adding Lunch activity and dummy lunch intstructor Set
instructorSet = set()

# add lunch activity for each subgroup
lunchActivityIdSet = set()
lunchId = activityId+1
lunchInFourDaysXML = ''

for sg in studentGroups:
    
    for s in studentGroups[sg]:
        lunchInFourDaysXML = lunchInFourDaysXML + '<ConstraintMinDaysBetweenActivities>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Weight_Percentage>100</Weight_Percentage>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Consecutive_If_Same_Day>true</Consecutive_If_Same_Day>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Number_of_Activities>4</Number_of_Activities>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Activity_Id>'+str(lunchId)+'</Activity_Id>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Activity_Id>'+str(lunchId+1)+'</Activity_Id>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Activity_Id>'+str(lunchId+2)+'</Activity_Id>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Activity_Id>'+str(lunchId+3)+'</Activity_Id>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<MinDays>1</MinDays>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Active>true</Active>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '\t<Comments></Comments>\n'
        lunchInFourDaysXML = lunchInFourDaysXML + '</ConstraintMinDaysBetweenActivities>\n'
    
        lXML = '<Activity>\n'
        dummyInstructor = 'Lunch'+s
        instructorSet.add(dummyInstructor)
        
        lXML = lXML + '\t<Teacher>'+dummyInstructor+'</Teacher>\n'
        lXML = lXML + '\t<Subject>Lunch</Subject>\n'
        lXML = lXML + '\t<Activity_Tag></Activity_Tag>\n'
        lXML = lXML + '\t<Students>'+s+'</Students>\n'
        lXML = lXML + '\t<Duration>2</Duration>\n'
        lXML = lXML + '\t<Total_Duration>8</Total_Duration>\n'
        
        for i in range(4): # four activity for lunch on M, T, W, Fri. The lunch on Thursday is automatically in break hours
            if (i == 0):
                lunchGroupId = lunchId
            lXMLi = lXML # each lunch period is a new actvity
            lXMLi = lXMLi + '\t<Id>'+str(lunchId)+'</Id>\n'
            lXMLi = lXMLi + '\t<Activity_Group_Id>'+str(lunchGroupId)+'</Activity_Group_Id>\n'
            lXMLi = lXMLi + '\t<Active>true</Active>\n'
            lXMLi = lXMLi + '\t<Comments></Comments>\n'
            lXMLi = lXMLi + '</Activity>\n'
            
            activityListXML = activityListXML + lXMLi
            lunchId = lunchId  + 1

activityListXML = activityListXML+ '<!-- SPACE FOR MORE ACTIVITIES -->\n'
activityListXML = activityListXML+ '</Activities_List>\n'

formattedData = re.sub(
        r"<Activities_List>(.*?)</Activities_List>", activityListXML,
        formattedData,flags=re.DOTALL)

# read instructos set
for cIndex, c in courseList.items():
    if 'lecSections' in c:
        for sId,s in c['lecSections'].items():
            instructorSet = instructorSet.union(set(s['instructors']))
    if 'tutSections' in c:
        for sId,s in c['tutSections'].items():
            instructorSet = instructorSet.union(set(s['instructors']))
    if 'labSections' in c:
        for sId,s in c['labSections'].items():
            instructorSet = instructorSet.union(set(s['instructors']))
            
#save the instructor set for creating their non available slots
with open('instructorSet.pickle', 'wb') as f:
    pickle.dump(instructorSet, f)


subjectListXML = '<Subjects_List>\n'
for cIndex in sorted(courseList):
    subjectListXML = subjectListXML + '<Subject>\n'
    subjectListXML = subjectListXML + '\t<Name>'+cIndex+'</Name>\n'
    subjectListXML = subjectListXML + '\t<Comments></Comments>\n'
    subjectListXML = subjectListXML + '</Subject>\n'
    
# add lunch subject
subjectListXML = subjectListXML + '<Subject>\n'
subjectListXML = subjectListXML + '\t<Name>Lunch</Name>\n'
subjectListXML = subjectListXML + '\t<Comments></Comments>\n'
subjectListXML = subjectListXML + '</Subject>\n'

subjectListXML = subjectListXML + '</Subjects_List>\n'
formattedData = re.sub(
        r"<Subjects_List>(.*?)</Subjects_List>", subjectListXML,
        formattedData,flags=re.DOTALL)

# add instute name
formattedData = re.sub(
        r"<Institution_Name>.*</Institution_Name>",
        '<Institution_Name>Shiv Nadar University</Institution_Name>',
        formattedData)

# add instute name
formattedData = re.sub(
        r"<Institution_Name>.*</Institution_Name>",
        '<Institution_Name>Shiv Nadar University</Institution_Name>',
        formattedData)

#days
timeTableDays = ['M','T','W','Th','F']

# replace default days 
daysTag = "<Days_List>\n"
daysTag = daysTag + "<Number_of_Days>"+str(len(timeTableDays))+"</Number_of_Days>\n"

for day in timeTableDays:
    daysTag = daysTag + "<Day><Name>"+ day + "</Name></Day>\n" 

daysTag = daysTag + "</Days_List>\n"

formattedData = re.sub(
        r"<Days_List>(.*?)</Days_List>", daysTag,
        formattedData,flags=re.DOTALL)

# replace default hours
hoursTag = "<Hours_List>\n"
hoursTag = hoursTag + "<Number_of_Hours>"+str(len(slots))+"</Number_of_Hours>\n"

for h in slots:
    hoursTag = hoursTag + "<Hour><Name>"+ h + "</Name></Hour>\n" 

hoursTag = hoursTag + "</Hours_List>\n"

formattedData = re.sub(
        r"<Hours_List>(.*?)</Hours_List>", hoursTag,
        formattedData,flags=re.DOTALL)


# fill in students list
formattedData = re.sub(
        r"<Students_List>(.*?)</Students_List>", studentsListXML,
        formattedData,flags=re.DOTALL)      

##----------------------------------------
#read roomsAndBuildingFile
with open('labRoomList.csv', 'r') as ff:
  reader = csv.reader(ff)
  roomsAndBuilding = list(reader)
 

buildingSet = set('');
labRoomCons = ''

tag = '<Rooms_List>\n'
for room in roomsAndBuilding[1:]:   # [1:] is for ignoring the first row
    
    buildingSet.add(room[2])
    if (room[2] == 'Lab'):
        labRoomCons = labRoomCons + '<ConstraintActivityTagPreferredRoom>\n \
    <Weight_Percentage>100</Weight_Percentage> \n \
    <Activity_Tag>'+room[0]+'</Activity_Tag> \n \
    <Room>'+room[0]+'</Room> \n \
    <Active>true</Active> \n \
    <Comments></Comments> \n \
</ConstraintActivityTagPreferredRoom>\n'
    
    tag = tag + '<Room> \n\
    <Name>'+room[0]+'</Name>\n \
    <Building>'+room[2]+'</Building>\n \
    <Capacity>'+room[1]+'</Capacity>\n \
    <Comments></Comments>\n </Room>\n '
tag = tag+ '</Rooms_List>\n'

#update file
formattedData = re.sub(
        r"<Rooms_List>(.*?)</Rooms_List>", tag,
        formattedData,flags=re.DOTALL)      

# add building list
tag = '<Buildings_List>\n'
for building in buildingSet:   # [1:] is for ignoring the first row
    tag = tag + '<Building>\n \
    <Name>'+building+'</Name> \n \
    <Comments></Comments> \n \
</Building>\n'
    
tag = tag+ '</Buildings_List>\n'
#update file
formattedData = re.sub(
        r"<Buildings_List>(.*?)</Buildings_List>", tag,
        formattedData,flags=re.DOTALL)      
#-------------------------------------------------------------

##--space constraint------------------------------------------



# basic compulsory constraint
spaceCons = '<Space_Constraints_List> \n \
<ConstraintBasicCompulsorySpace> \n \
    <Weight_Percentage>100</Weight_Percentage> \n \
    <Active>true</Active> \n \
    <Comments></Comments> \n \
</ConstraintBasicCompulsorySpace>\n'
spaceCons =spaceCons +  labRoomCons

# universal room constraint
#import roomsConstraint as roomConstraint
#spaceCons = spaceCons + roomConstraint.LEC1SpaceCons



spaceCons =spaceCons +  '</Space_Constraints_List>\n'

    
#update file
formattedData = re.sub(
        r"<Space_Constraints_List>(.*?)</Space_Constraints_List>", spaceCons,
        formattedData,flags=re.DOTALL)      
    


######################################################
## -- end of space constratint



#### time constraints ##############################################333

# basic compulsory time constraint
tag = '<Time_Constraints_List>\n\
<ConstraintBasicCompulsoryTime>\n\
    <Weight_Percentage>100</Weight_Percentage>\n\
    <Active>true</Active>\n\
    <Comments></Comments>\n\
</ConstraintBasicCompulsoryTime>\n'

## add Th 12-2 break time
#tag = tag + '<ConstraintBreakTimes> \n\
#	<Weight_Percentage>100</Weight_Percentage> \n \
#	<Number_of_Break_Times>4</Number_of_Break_Times> \n \
#	<Break_Time> \n \
#		<Day>Th</Day> \n \
#		<Hour>12:00</Hour> \n \
#	</Break_Time> \n \
#	<Break_Time> \n \
#		<Day>Th</Day> \n \
#		<Hour>12:30</Hour> \n \
#	</Break_Time> \n \
#	<Break_Time> \n \
#		<Day>Th</Day> \n \
#		<Hour>13:00</Hour> \n \
#	</Break_Time> \n \
#    	<Break_Time> \n \
#		<Day>Th</Day> \n \
#		<Hour>13:30</Hour> \n \
#	</Break_Time> \n \
#	<Active>true</Active> \n \
#	<Comments></Comments> \n \
#</ConstraintBreakTimes>\n'

# add Th 12-2 break time
tag = tag + '<ConstraintBreakTimes> \n\
	<Weight_Percentage>100</Weight_Percentage> \n \
	<Number_of_Break_Times>4</Number_of_Break_Times> \n \
	<Break_Time> \n \
		<Day>Th</Day> \n \
		<Hour>12:00</Hour> \n \
	</Break_Time> \n \
	<Break_Time> \n \
		<Day>Th</Day> \n \
		<Hour>12:30</Hour> \n \
	</Break_Time> \n \
	<Break_Time> \n \
		<Day>Th</Day> \n \
		<Hour>13:00</Hour> \n \
	</Break_Time> \n \
    	<Break_Time> \n \
		<Day>Th</Day> \n \
		<Hour>13:30</Hour> \n \
	</Break_Time> \n \
	<Active>true</Active> \n \
	<Comments></Comments> \n \
</ConstraintBreakTimes>\n'




with open('courses.pickle', 'wb') as f:
    pickle.dump(courseList, f)

with open('slots.pickle', 'wb') as f:
    pickle.dump(slots,f)
    


#from lunch5daysXML import lunchConsTag
from lunchXML import lunchConsTag

tag = tag + lunchConsTag

# adding constraint of same lectures on diff days to be on same time
for cIndex, c in courseList.items():
    if 'lecSections' in c:
        for lIndex, l in c['lecSections'].items():
            # same lecture on diff days should have same time slots
            if 'ids' in l:
                tag = tag + '<ConstraintActivitiesSameStartingHour>\n'
                tag = tag + '\t<Weight_Percentage>100</Weight_Percentage>\n'
                tag = tag + '\t<Number_of_Activities>'+str(len(l['ids']))+'</Number_of_Activities>\n'
                
                for id in l['ids']:
                    tag = tag+ '\t\t<Activity_Id>'+str(id)+'</Activity_Id>\n'
                tag = tag + '\t<Active>true</Active>\n'
                tag = tag + '\t<Comments></Comments>\n'
                tag = tag + '</ConstraintActivitiesSameStartingHour>\n'

            # slots in FET are of half hours. 1 hour class is 2 consecutive slot and 
            # a 1.5 hours class  is consecutive 3 slots.
            if 'ids' in l:
                tag = tag + '<ConstraintMinDaysBetweenActivities> \n'
                tag = tag + '\t<Weight_Percentage>100</Weight_Percentage>\n'
                tag = tag + '\t<Consecutive_If_Same_Day>true</Consecutive_If_Same_Day>\n'
                tag = tag + '\t<Number_of_Activities>'+str(len(l['ids']))+'</Number_of_Activities>\n'
                                
                for id in l['ids']:
                    tag = tag+ '\t\t<Activity_Id>'+str(id)+'</Activity_Id>\n'
                tag = tag + '\t<MinDays>2</MinDays>\n'
                tag = tag + '\t<Active>true</Active>\n'
                tag = tag + '\t<Comments></Comments>\n'
                tag = tag + '</ConstraintMinDaysBetweenActivities>\n'
tag = tag+ lunchInFourDaysXML

# add CCC overlapping constratint
#import CCCsameSlot as ov
##import overlappingCCCstring as ov
##tag = tag+ov.x
#tag = tag +ov.coursesOverlappingXML

#from minimalGapsForTeachers import globalMinGapXML
#tag = tag + globalMinGapXML

# Ajit: Jul 10, students set not availability is ignored. Completely determined by faculty availability
import studentsNotAvailableSlots as sna
tag = tag+ sna.studentsFreeTimeXML

#import teachersNotAvailableSlots as tna
import teachersNonAvailabilityAndSeminars as tna
tag = tag+tna.x

# large lectures early constrints
#import lecturesPrefferedinEarlyslots as lecEarlyCons
#tag = tag + lecEarlyCons.LEC1early


# teachers max hours continuously constraint
#import teacherMaxContinuousHoursDaily as tMaxContinuous
#tag = tag + tMaxContinuous.consList

# teachers max number of working day constraint
#import teachersMaxWorkingDay as teacherMaxDay
#tag = tag + teacherMaxDay.teacherMaxDayConsXML


# courses with preferred slots 
# USE IN RARE CASE
from coursesPreferredSlots import prefSlotXml
tag = tag + prefSlotXml


# end of time constraint
tag = tag + '</Time_Constraints_List>\n'
#tag = tag+'</Time_Constraints_List>\n'
##  end time constraints

# write your content in n new file
formattedData = re.sub(
        r"<Time_Constraints_List>(.*?)</Time_Constraints_List>",tag ,
        formattedData,flags=re.DOTALL)      



teachersXML = '<Teachers_List>\n'
for i in sorted(instructorSet):
    teachersXML = teachersXML + '<Teacher>\n'
    teachersXML = teachersXML + '\t<Name>'+i+'</Name>\n'
    teachersXML = teachersXML + '\t<Target_Number_of_Hours>0</Target_Number_of_Hours>\n'
    teachersXML = teachersXML + '\t<Qualified_Subjects></Qualified_Subjects>\n'
    teachersXML = teachersXML + '\t<Comments></Comments>\n'
    teachersXML = teachersXML + '</Teacher>\n'

teachersXML = teachersXML + '</Teachers_List>\n'
# write your content in n new file
formattedData = re.sub(
        r"<Teachers_List>(.*?)</Teachers_List>",teachersXML ,
        formattedData,flags=re.DOTALL)      


# write activity tags in fet
activityTagListXML = '<Activity_Tags_List>\n'

for a in sorted(activityTagSet):
    activityTagListXML = activityTagListXML + '<Activity_Tag>\n'
    activityTagListXML = activityTagListXML + '\t<Name>'+a+'</Name>\n'
    activityTagListXML = activityTagListXML + '\t<Printable>true</Printable>\n'
    activityTagListXML = activityTagListXML + '\t<Comments></Comments>\n'
    activityTagListXML = activityTagListXML + '</Activity_Tag>\n'

activityTagListXML = activityTagListXML + '</Activity_Tags_List>\n'    
formattedData = re.sub(
        r"<Activity_Tags_List>(.*?)</Activity_Tags_List>",activityTagListXML,
        formattedData,flags=re.DOTALL)      

## write file

f = open(fetFileName,'w+')
f.write(formattedData)
f.close

dayFile = 'trash.xml'
g = open(dayFile,'w')
g.write("trash")
g.close


    