#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 01:28:42 2019

@author: ajit
"""

import pickle
coursesPickle = open('courses.pickle','rb')
courses = pickle.load(coursesPickle) 

def favSlotXML(id,day,hour,weight):
    activityIdPreferredTimeXML = '<ConstraintActivityPreferredStartingTime>\n\
    	<Weight_Percentage>WEIGHT</Weight_Percentage>\n\
    	<Activity_Id>actID</Activity_Id>\n\
    	<Preferred_Day>favDAY</Preferred_Day>\n\
    	<Preferred_Hour>favHour</Preferred_Hour>\n\
    	<Permanently_Locked>false</Permanently_Locked>\n\
    	<Active>true</Active>\n\
    	<Comments></Comments>\n\
    </ConstraintActivityPreferredStartingTime>\n'
    activityIdPreferredTimeXML = activityIdPreferredTimeXML.replace('actID',str(id))
    activityIdPreferredTimeXML = activityIdPreferredTimeXML.replace('WEIGHT',str(weight))
    activityIdPreferredTimeXML = activityIdPreferredTimeXML.replace('favDAY',str(day))
    activityIdPreferredTimeXML = activityIdPreferredTimeXML.replace('favHour',str(hour))
    return activityIdPreferredTimeXML
    
coursesWithPreferredSlot = {
        'EED206': {'LEC1' :{'days' : ['M','W','F'], 'hour': '08:00', 'weight':100}},
        'MAT240': {'LEC1' :{'days' : ['T','Th'], 'hour': '10:30', 'weight' :100}},
        'MAT442': {'LEC1' :{'days' : ['T','Th'], 'hour': '14:00', 'weight' :100}},       
        }

prefSlotXml = ''
for c in coursesWithPreferredSlot:
    days = coursesWithPreferredSlot[c]['LEC1']['days']
    hour = coursesWithPreferredSlot[c]['LEC1']['hour']
    w = coursesWithPreferredSlot[c]['LEC1']['weight']
    nDays = len(days)
    ids = sorted(list(courses[c]['lecSections']['LEC1']['ids']))
    nClass = len(ids)
    if nClass != nDays:
        print(c, 'not slottable. Check fav slot parameters')
        continue
    for i in range(nClass):
        prefSlotXml = prefSlotXml+ favSlotXML(ids[i],days[i],hour,w)
        
        
    

    




