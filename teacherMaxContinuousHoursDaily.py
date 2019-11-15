#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 00:24:16 2019

@author: ajit
"""
## INPUT
#----------------------------------------------------------------------
insMaxContinuousList = {
        'ENG240AND342Instructor':{'weight':100, 'numHours':5},
        'J  Venkatramani[20500736]':{'weight':100, 'numHours':8},
        'Sathi Rajesh Reddy[20500731]':{'weight':100, 'numHours':8},
        'Shalini  Rankavat[20501010]':{'weight':100, 'numHours':8},
        'Anirban  Ghosh[20500908]':{'weight':100, 'numHours':5},
        'Koyeli   Mapa[20500426]': {'weight':100, 'numHours':6},
        'Amber  Habib[20500009]': {'weight':100, 'numHours':6},
        'Vikash  Kumar[20500361]': {'weight':100, 'numHours':8},
        'Prakash  Kumar[20500290]': {'weight':100, 'numHours':8},
        'Amit  Ray[20500123]': {'weight':100, 'numHours':8},
        'Shahid  Jamal[20500122]': {'weight':100, 'numHours':8},
        }
#----------------------------------------------------------------------

import pickle
instructorSetPickle = open('instructorSet.pickle','rb')
instructorSet = pickle.load(instructorSetPickle)


maxContXMLtemplate = '<ConstraintTeacherMaxHoursContinuously>\n\
	<Weight_Percentage>CONSWEIGHT</Weight_Percentage>\n\
	<Teacher_Name>CONSINSTRUCTOR</Teacher_Name>\n\
	<Maximum_Hours_Continuously>NUMHOURS</Maximum_Hours_Continuously>\n\
	<Active>true</Active>\n\
	<Comments></Comments>\n\
</ConstraintTeacherMaxHoursContinuously>\n'



consList = ''

for i in instructorSet:
    if i in insMaxContinuousList:
        w = str(insMaxContinuousList[i]['weight'])
        numContinuousHours = str(insMaxContinuousList[i]['numHours'])
    else:
        w = '100'
        numContinuousHours = '6'

    iCons = maxContXMLtemplate
    iCons = iCons.replace('CONSWEIGHT',w)
    iCons = iCons.replace('CONSINSTRUCTOR', i)
    iCons = iCons.replace('NUMHOURS', numContinuousHours)
    
    consList = consList + iCons
    
    
