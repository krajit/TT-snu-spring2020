#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 23:36:14 2019

@author: ajit
"""

import pickle
instructorSetPickle = open('instructorSet.pickle','rb')
instructorSet = pickle.load(instructorSetPickle) 


slotsPickle = open('slots.pickle','rb')
slots = pickle.load(slotsPickle)


days = ['M','T','W','Th','F']

import xlrd
instructorsOnCampus = set()
instructorsOnCampusFile = "InstructorsOnCampus.xlsx"
wb = xlrd.open_workbook(instructorsOnCampusFile) 
sheet = wb.sheet_by_index(0) # get first sheet
for i in range(1,sheet.nrows):    
    instructorsOnCampus.add(sheet.cell_value(i,0))

        
teachersNotAvailalbeSlots = {
        'Divya  Shrivastava[20500160]':{'09:00','09:30'},
        'Ajit  Kumar[20500008]':{'09:00','09:30'},
        'Ranendra Narayan Biswas[20500321]': {'13:00','13:30'},
        'Rohit  Singh[20501073]': {'13:00','13:30'},
        'Upendra Kumar Pandey[20501071]': {'13:00','13:30'},
        'Sonal  Singhal[20500080]': {'13:00','13:30'},
        'Sumit Tiwari': {'13:00','13:30'},
        'harpreet  Singh Grewal[20500440]':{'08:00','09:00','09:00','09:30'},
        'Gyan  Vikash[20500145]':{'09:00','09:30'},
        'Sri Krishna Jayadev Magani[20500054]': {'09:00','09:30'},
        'Sandeep Sen': set(slots[12:]),
        'Pooja  Malik[20500448]':{'13:00','13:30'},
        'Amber  Habib[20500009]':{'13:00','13:30'},
        'Lal Mohan Saha[20500014]':{'13:00','13:30'},
        }

teachersNotAvailalbeDays = {
        'Sanjeev  Agrawal[20500033]' : ['M'],
        'Jai Prakash Gupta[20500662]' : ['M'],
        }

genNonAvailability = {'M':{'08:00', '08:30', '17:00', '17:30'},
                      'T':{'08:00', '08:30', '17:00', '17:30'},
                      'W':{'08:00', '08:30', '17:00', '17:30'},
                      'Th':{'08:00', '08:30', '17:00', '17:30'},
                      'F':{'08:00', '08:30', '17:00', '17:30'}}

#onCampusNonAvailability = {'M':{'08:00', '08:30'},
#                      'T':{'08:00', '08:30' },
#                      'W':{'08:00', '08:30'},
#                      'Th':{'08:00', '08:30'},
#                      'F':{'08:00', '08:30'}}
        
onCampusNonAvailability = {'M':set(),
                      'T':set(),
                      'W':set(),
                      'Th':set(),
                      'F':set()}


# dept seminar slots
deptNonAvailability = {
        'School of Natural Sciences - Physics' : {'T':{'15:00','15:30','16:00'}},
        'School of Natural Sciences - Mathematics': {'T':{'15:30','16:00','16:30'}}
        }

deptListOfInstructorsPickle = open('deptListOfInstructors.pickle','rb')
deptListOfInstructors = pickle.load(deptListOfInstructorsPickle)


import copy
x = ''
for i in instructorSet:
    
    #check if person live on compus
    iLiveOnCampus = False
    for j in instructorsOnCampus:
        if j[-10:] == i[-10:]:
            iLiveOnCampus = True
            continue
        
    if iLiveOnCampus:
        iNonAvailability = copy.deepcopy(onCampusNonAvailability)
    else:
        iNonAvailability = copy.deepcopy(genNonAvailability)
        
    
    # tweak iNonAvailability slots
    if i in teachersNotAvailalbeSlots:
        for d in ['M','T','W','Th','F']:
            iNonAvailability[d] = iNonAvailability[d].union(teachersNotAvailalbeSlots[i])

            
    # add whole slots on non availalbe days
    if i in teachersNotAvailalbeDays:
        for d in teachersNotAvailalbeDays[i]:
            iNonAvailability[d] = set(slots)
            
    # check if i belong to any dept who wants a seminar slot
    department = ''
    for dept in deptListOfInstructors:
        if i in deptListOfInstructors[dept]:
            department = dept
    
    # expand non availability slots for the entire dept
    if department in deptNonAvailability:
        extraFreeSlot = deptNonAvailability[department]
        for d in extraFreeSlot:
            iNonAvailability[d] = iNonAvailability[d].union(extraFreeSlot[d])
            
    numSlots = 0
    slotsXML = ''
    for d in iNonAvailability:
        numSlots = numSlots +len(iNonAvailability[d])
        for s in iNonAvailability[d]:
            slotsXML = slotsXML+ '\t<Not_Available_Time>\n\t\t<Day>'+d+'</Day>\n\t\t<Hour>'+s+'</Hour>\n\t</Not_Available_Time>\n'
        
        # teacher not available slot
    xi = "<ConstraintTeacherNotAvailableTimes>\n\
	<Weight_Percentage>100</Weight_Percentage>\n\
	<Teacher>"+i+"</Teacher>\n\
	<Number_of_Not_Available_Times>"+str(numSlots)+"</Number_of_Not_Available_Times>\n"
    
    xi = xi + slotsXML
    xi = xi + "	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintTeacherNotAvailableTimes>\n"
    x = x+xi
        
