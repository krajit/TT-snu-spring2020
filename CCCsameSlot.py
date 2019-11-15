#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 03:50:06 2019

@author: ajit
"""
import pickle
coursesPickle = open('courses.pickle','rb')
courses = pickle.load(coursesPickle) 

twoOverlappingTemplate = "<ConstraintActivitiesSameStartingTime> \n\
	<Weight_Percentage>100</Weight_Percentage> \n\
	<Number_of_Activities>2</Number_of_Activities> \n \
	<Activity_Id>item1</Activity_Id> \n\
	<Activity_Id>item2</Activity_Id>\n\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintActivitiesSameStartingTime>\n"



x1 =  "<ConstraintActivitiesSameStartingTime> \n\
	<Weight_Percentage>100</Weight_Percentage>\n"
x2 =  "<ConstraintActivitiesSameStartingTime> \n\
	<Weight_Percentage>100</Weight_Percentage>\n"
  
  


def overlapXML(c1,c2):    
    # make sure these two courses are overlappable
    lids1 = []
    lids2 = []
    tids1 = []
    tids2 = []
    pids1 = []
    pids2 = []
        
    if 'lecSections' in courses[c1]:
        lids1 = list(courses[c1]['lecSections']['LEC1']['ids'])
    if 'lecSections' in courses[c2]:
        lids2 = list(courses[c2]['lecSections']['LEC1']['ids'])
    if 'tutSections' in courses[c1]:
        tids1 = list(courses[c1]['tutSections']['TUT1']['ids'])
    if 'tutSections' in courses[c2]:
        tids2 = list(courses[c2]['tutSections']['TUT1']['ids'])
    if 'labSections' in courses[c1]:
        pids1 = list(courses[c1]['labSections']['PRAC1']['ids'])
    if 'labSections' in courses[c2]:
        pids2 = list(courses[c2]['labSections']['PRAC1']['ids'])
        
    ltpids1 = lids1 + tids1 + pids1
    ltpids2 = lids2 + tids2 + pids2
        
    if (len(ltpids1) != len(ltpids2)):
        print("can't overlap", c1, ' and ', c2)
        print(ltpids1,ltpids2)
    out = ''
    for j in range(len(ltpids1)):
        outj = twoOverlappingTemplate
        outj = outj.replace('item1',str(ltpids1[j]))
        outj = outj.replace('item2',str(ltpids2[j]))
        out = out+outj
    return out


def overlapOnlyLecturesXML(c1,c2):    
    # make sure these two courses are overlappable
    lids1 = []
    lids2 = []
        
    if 'lecSections' in courses[c1]:
        lids1 = list(courses[c1]['lecSections']['LEC1']['ids'])
    if 'lecSections' in courses[c2]:
        lids2 = list(courses[c2]['lecSections']['LEC1']['ids'])
        
    if (len(lids1) != len(lids2)):
        print("can't overlap", c1, ' and ', c2)
        print(lids1,lids2)
    out = ''
    for j in range(len(lids1)):
        outj = twoOverlappingTemplate
        outj = outj.replace('item1',str(lids1[j]))
        outj = outj.replace('item2',str(lids2[j]))
        out = out+outj
    return out


def overlapIds(id1, id2):
    out = twoOverlappingTemplate
    out = out.replace('item1',id1)
    out = out.replace('item2',id2)
    return out
    


#MAT494_overlaps_CSD310 = overlapXML('CSD310','MAT494')
#MAT440overlapsMAT424 = overlapXML('MAT440', 'MAT424')

mathOverLap1 = overlapXML('MAT390', 'MAT440')    
mathOverLap2 = overlapXML('MAT422', 'MAT494')    
mathOverLap3 = overlapOnlyLecturesXML('MAT399','MAT442')
coursesOverlappingXML = mathOverLap1 + mathOverLap2 + mathOverLap3

coursesOverlappingXML = coursesOverlappingXML + overlapXML('MED308','MED410')
coursesOverlappingXML = coursesOverlappingXML + overlapXML('MED318','MED409')

# overlap CSD411 lecture and MAT494 lab
id1 = str(list(courses['CSD411']['lecSections']['LEC1']['ids'])[0])
id2 = str(list(courses['MAT494']['labSections']['PRAC1']['ids'])[0])
coursesOverlappingXML = coursesOverlappingXML + overlapIds(id1,id2)
    




