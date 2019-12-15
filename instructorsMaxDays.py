#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 22:45:36 2019

@author: ajit
"""


# import slots and courses list from COS2FET
import pickle
instructorSetPickle = open('instructorSet.pickle','rb')
instructorSet = pickle.load(instructorSetPickle) 

dumpString = ''

teacherMaxDayXML = '<ConstraintTeacherMaxDaysPerWeek>\n\
	<Weight_Percentage>100</Weight_Percentage>\n\
	<Teacher_Name>TEACHERNAME</Teacher_Name>\n\
	<Max_Days_Per_Week>4</Max_Days_Per_Week>\n\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintTeacherMaxDaysPerWeek>\n'

for i in instructorSet:
    if "Lunch" in i:
        continue
    ti = teacherMaxDayXML.replace('TEACHERNAME',i)
    dumpString = dumpString + ti
    

f = open("instructorMaxDays.xml",'w+')
f.write(dumpString)
f.close
