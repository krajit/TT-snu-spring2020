#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 00:35:43 2019

@author: ajit
"""

import pickle
studentGroupsPickle = open('studentGroups.pickle','rb')
studentGroups = pickle.load(studentGroupsPickle) 

studentsFreeSlotTemplate = "<ConstraintStudentsSetNotAvailableTimes>\n\
	<Weight_Percentage>100</Weight_Percentage>\n\
	<Students>GROUPNAME</Students>\n\
	<Number_of_Not_Available_Times>NUMSLOTS</Number_of_Not_Available_Times>\n\
	BREAKSLOTS\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintStudentsSetNotAvailableTimes>\n" 

studentsFreeSlot = {
        'PHY4' :{'day': 'T', 'hours': {'15:00','15:30','16:00'}}
        }


studentsFreeTimeXML = ''

for si in studentsFreeSlot:
    siXML = studentsFreeSlotTemplate
    siXML = siXML.replace('GROUPNAME',si)
    siXML = siXML.replace('NUMSLOTS',str(len(studentsFreeSlot[si]['hours'])))
    day = studentsFreeSlot[si]['day']
    hours = studentsFreeSlot[si]['hours']    
    siBreakTime = ''
    for h in hours:
        siBreakTime = siBreakTime +'<Not_Available_Time>\n\
		<Day>'+day+'</Day>\n\
		<Hour>'+h+'</Hour>\n\
	</Not_Available_Time>\n'    
    siXML = siXML.replace('BREAKSLOTS',siBreakTime)
    
    studentsFreeTimeXML = studentsFreeTimeXML + siXML
    
    
    

