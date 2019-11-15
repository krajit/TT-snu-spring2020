#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 02:50:30 2019

@author: ajit
"""
import pickle
instructorSetPickle = open('instructorSet.pickle','rb')
instructorSet = pickle.load(instructorSetPickle)


gapsXMLTemplate = '<ConstraintTeacherMaxGapsPerDay>\n\
	<Weight_Percentage>100</Weight_Percentage>\n\
	<Teacher_Name>TEACHERNAME</Teacher_Name>\n\
	<Max_Gaps>MAXGAP</Max_Gaps>\n\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintTeacherMaxGapsPerDay>\n'


globalMinGapXML = ''
generalGap = 1

specialInstructorsGaps = {
        'Sudeepto  Bhattacharya[20500090]' : 10,      
        }

for i in instructorSet:
    iGap = generalGap
    if i in specialInstructorsGaps:
        iGap = specialInstructorsGaps[i]
    
    iXML = gapsXMLTemplate
    iXML = iXML.replace('TEACHERNAME',i)
    iXML = iXML.replace('MAXGAP',str(iGap))
    
    globalMinGapXML = globalMinGapXML + iXML
        

