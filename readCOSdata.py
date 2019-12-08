
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 15:11:10 2019

@author: ajit
"""
import xlrd

import re

import pickle
studentSubGroupsPickle = open('studentSubGroups.pickle','rb')
studentSubGroups = pickle.load(studentSubGroupsPickle)


COSfilePath = "COS.xlsx"
wb = xlrd.open_workbook(COSfilePath) 
sheet = wb.sheet_by_index(0) # get first sheet

# column heading numbers
deptCol = 1
CourseCode	=	2
CourseTitle	=	3
CourseType	=	5
OpenAsUWE = 6
CourseCapacity	=	18
LectureHoursPerWeek	=	19
TutorialHoursPerWeek	=	20
PracticalHoursPerWeek	=	21
LectureDuration	=	22
LectureSections	=	23
TutorialSections	=	24
PracticalSections	=	25
LectureInstructors	=	26
TutorialInstructors	=	27
PracticalInstructors	=	28
LabRoomNumber	=	29
LabCapacity	=	30
CourseCoordinator	=	38
LectureTag1Col = 55
LectureTag2Col = 56   # put same tags to overlapping lectures and tutorials
UWELecCol = 60
UWETutCol = 61
UWEPracCol = 62
skipThisCourse = 63


courseList = dict()
deptListOfInstructors = dict()

for i in range(2,sheet.nrows):    
    cCode = sheet.cell_value(i,CourseCode)
    
    #skip some rows
    if (sheet.cell_type(i,skipThisCourse) != xlrd.XL_CELL_EMPTY):
        continue

    
    if (sheet.cell_type(i,deptCol) != xlrd.XL_CELL_EMPTY):
        dept = sheet.cell_value(i,deptCol)
    
    if dept not in deptListOfInstructors:
        deptListOfInstructors[dept] = set()
        
    
    if cCode not in courseList:
        courseList[cCode] = dict()
        courseList[cCode]['Title'] = sheet.cell_value(i,CourseTitle)
        courseList[cCode]['CourseType'] = sheet.cell_value(i,CourseType)
        courseList[cCode]['CourseCapacity'] = int(sheet.cell_value(i,CourseCapacity))
        courseList[cCode]['department'] = dept
        courseList[cCode]['openAsUWE'] = sheet.cell_value(i,OpenAsUWE)
       
        if (sheet.cell_type(i,LectureDuration) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['LectureDuration'] = int(2*float(sheet.cell_value(i,LectureDuration)))
        
        
        if (sheet.cell_type(i,LectureHoursPerWeek) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['LectureHoursPerWeek'] = int(2*float(sheet.cell_value(i,LectureHoursPerWeek)))
        else:
            courseList[cCode]['LectureHoursPerWeek'] = 0
            
        if (sheet.cell_type(i,TutorialHoursPerWeek) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['TutorialHoursPerWeek'] = int(2*float(sheet.cell_value(i,TutorialHoursPerWeek)))
        else:
            courseList[cCode]['TutorialHoursPerWeek'] = 0 
            
        if (sheet.cell_type(i,PracticalHoursPerWeek) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['PracticalHoursPerWeek'] = int(2*float(sheet.cell_value(i,PracticalHoursPerWeek)))
        else:
            courseList[cCode]['PracticalHoursPerWeek'] = 0
            
            
    if (sheet.cell_type(i,LectureSections) != xlrd.XL_CELL_EMPTY):
        if 'lecSections' not in courseList[cCode]:
            courseList[cCode]['lecSections'] = dict()

        lecStudentsColumn = 51
        seci = sheet.cell_value(i,LectureSections)
        courseList[cCode]['lecSections'][seci] = dict()
        
        
        courseList[cCode]['lecSections'][seci]['instructors'] = sheet.cell_value(i,LectureInstructors).split(',\n')
        courseList[cCode]['lecSections'][seci]['instructors'][-1] = courseList[cCode]['lecSections'][seci]['instructors'][-1][0:-1] 
        
        
        deptListOfInstructors[dept] = deptListOfInstructors[dept].union(courseList[cCode]['lecSections'][seci]['instructors'])
        courseList[cCode]['lecSections'][seci]['potentialStudents'] = set()
        if (sheet.cell_type(i,lecStudentsColumn) != xlrd.XL_CELL_EMPTY):
            if (sheet.cell_value(i,lecStudentsColumn) != ''):
                courseList[cCode]['lecSections'][seci]['potentialStudents'] = set(sheet.cell_value(i,lecStudentsColumn).split(','))
        courseList[cCode]['lecSections'][seci]['students'] = set()
        
        if 'activityTags' not in courseList[cCode]['lecSections'][seci]:
            courseList[cCode]['lecSections'][seci]['activityTags'] = set()
            
        if (sheet.cell_type(i,LectureTag1Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['lecSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag1Col))
            
        if (sheet.cell_type(i,LectureTag2Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['lecSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag2Col))
           
           
        # add UWE studetns i
        if (sheet.cell_type(i,UWELecCol) != xlrd.XL_CELL_EMPTY):
            studentsList =  sheet.cell_value(i,UWELecCol)
            studentsList = studentsList.split(',')
            studentSet = set()
            for s in studentsList:
                #ss = studentSet.union(set(studentSubGroups[s].split(',')))
                ss = studentSet.union(set(studentsList))
                courseList[cCode]['lecSections'][seci]['students'] = courseList[cCode]['lecSections'][seci]['students'].union(ss)
                
            
 #           courseList[cCode]['lecSections'][seci]['UWEStudents'].union(set(sheet.cell_value(i,UWELecCol).split(',')))
        
    
    if (sheet.cell_type(i,TutorialSections) != xlrd.XL_CELL_EMPTY):
        if 'tutSections' not in courseList[cCode]:
            courseList[cCode]['tutSections'] = dict()

        tutStudentsColumn = 52
        seci = sheet.cell_value(i,TutorialSections)
        courseList[cCode]['tutSections'][seci] = dict()

        courseList[cCode]['tutSections'][seci]['instructors'] = sheet.cell_value(i,TutorialInstructors).split(',\n')
        courseList[cCode]['tutSections'][seci]['instructors'][-1] = courseList[cCode]['tutSections'][seci]['instructors'][-1][0:-1] 
        deptListOfInstructors[dept] = deptListOfInstructors[dept].union(courseList[cCode]['tutSections'][seci]['instructors'])



        courseList[cCode]['tutSections'][seci]['potentialStudents'] = set()
        if (sheet.cell_type(i,tutStudentsColumn) != xlrd.XL_CELL_EMPTY):        
            if (sheet.cell_value(i,tutStudentsColumn) != ''):
                courseList[cCode]['tutSections'][seci]['potentialStudents'] = set(sheet.cell_value(i,tutStudentsColumn).split(','))
        courseList[cCode]['tutSections'][seci]['students'] = set()
        
        
        if 'activityTags' not in courseList[cCode]['tutSections'][seci]:
            courseList[cCode]['tutSections'][seci]['activityTags'] = set()
        
        if (sheet.cell_type(i,LectureTag1Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['tutSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag1Col))
        if (sheet.cell_type(i,LectureTag2Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['tutSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag2Col))



        
        # add UWE studetns i
        if (sheet.cell_type(i,UWETutCol) != xlrd.XL_CELL_EMPTY):
            studentsList =  sheet.cell_value(i,UWETutCol)
            studentsList = studentsList.split(',')
            studentSet = set()
            for s in studentsList:
                #ss = studentSet.union(set(studentSubGroups[s].split(',')))
                ss = studentSet.union(set(studentsList))
                courseList[cCode]['tutSections'][seci]['students'] = courseList[cCode]['tutSections'][seci]['students'].union(ss)


            
    if (sheet.cell_type(i,PracticalSections) != xlrd.XL_CELL_EMPTY):
        if 'labSections' not in courseList[cCode]:
            courseList[cCode]['labSections'] = dict()

        labStudentsColumn = 53
        seci = sheet.cell_value(i,PracticalSections)
        courseList[cCode]['labSections'][seci] = dict()
        courseList[cCode]['labSections'][seci]['instructors'] = sheet.cell_value(i,PracticalInstructors).split(',\n')
        courseList[cCode]['labSections'][seci]['instructors'][-1] = courseList[cCode]['labSections'][seci]['instructors'][-1][0:-1] 


        deptListOfInstructors[dept] = deptListOfInstructors[dept].union(courseList[cCode]['labSections'][seci]['instructors'])
        courseList[cCode]['labSections'][seci]['potentialStudents'] = set()
        if (sheet.cell_type(i,labStudentsColumn) != xlrd.XL_CELL_EMPTY):        
            if (sheet.cell_value(i,labStudentsColumn) != ''):
                courseList[cCode]['labSections'][seci]['potentialStudents'] = set(sheet.cell_value(i,labStudentsColumn).split(','))
        
        courseList[cCode]['labSections'][seci]['room'] =  sheet.cell_value(i,LabRoomNumber)
        courseList[cCode]['labSections'][seci]['students'] = set()
    
        if 'activityTags' not in courseList[cCode]['labSections'][seci]:
            courseList[cCode]['labSections'][seci]['activityTags'] = set()
        
        if (sheet.cell_type(i,LectureTag1Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['labSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag1Col))
        if (sheet.cell_type(i,LectureTag2Col) != xlrd.XL_CELL_EMPTY):
            courseList[cCode]['labSections'][seci]['activityTags'].add(sheet.cell_value(i,LectureTag2Col))

    
            # add UWE studetns i
        if (sheet.cell_type(i,UWEPracCol) != xlrd.XL_CELL_EMPTY):
            studentsList =  sheet.cell_value(i,UWEPracCol)
            studentsList = studentsList.split(',')
            studentSet = set()
            for s in studentsList:
                #ss = studentSet.union(set(studentSubGroups[s].split(',')))
                ss = studentSet.union(set(studentsList))
                courseList[cCode]['labSections'][seci]['students'] = courseList[cCode]['labSections'][seci]['students'].union(ss)


# dump deptwise list of faculty
with open('deptListOfInstructors.pickle', 'wb') as f:
    pickle.dump(deptListOfInstructors, f)