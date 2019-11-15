#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 02:43:10 2019

@author: ajit
"""

teachMaxWorkingDayXMLtemplate = '<ConstraintTeacherMaxDaysPerWeek>\n\
	<Weight_Percentage>100</Weight_Percentage>\n\
	<Teacher_Name>TEACHERNAME</Teacher_Name>\n\
	<Max_Days_Per_Week>NUMDAY</Max_Days_Per_Week>\n\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintTeacherMaxDaysPerWeek>\n'


teachersWithMaxDayConstraint = {
        'Jabin Thomas Jacob[20501014]' : 3, # num days
        'Kaveri   Gill[20500669]': 3
        }

teacherMaxDayConsXML = ''

for t in teachersWithMaxDayConstraint:
    numDays = str(teachersWithMaxDayConstraint[t])
    XMLi = teachMaxWorkingDayXMLtemplate
    XMLi = XMLi.replace('TEACHERNAME',t)
    XMLi = XMLi.replace('NUMDAY',numDays)
    
    teacherMaxDayConsXML = teacherMaxDayConsXML + XMLi 
    