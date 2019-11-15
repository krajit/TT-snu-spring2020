#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:21:02 2019

@author: ajit
"""

# prepare student groups
import xlrd
studentsGroupFile = "GroupsandSubgroups.xlsx"
wb = xlrd.open_workbook(studentsGroupFile) 
sheet = wb.sheet_by_index(0) # get first sheet
studentGroups = dict()

for i in range(1,sheet.nrows):
    y = sheet.cell_value(i,0)
    yeari = 'year'+y
    
    sg = ''
    if sheet.cell_type(i,3) == xlrd.XL_CELL_EMPTY:
        sg = sheet.cell_value(i,2)
        if yeari not in studentGroups:
            studentGroups[yeari] =set()
            studentGroups[yeari].add(sg)
        else:
            studentGroups[yeari].add(sg)
    else:
        sg = sheet.cell_value(i,3)
        sg = sg.split(',')
        tempSg = ''
        for s in sg:
            if yeari not in studentGroups:
                studentGroups[yeari] =set()
                studentGroups[yeari].add(s[0:5])
            else:
                studentGroups[yeari].add(s[0:5])
                
                
# create students subgroups for adding students in UWE courses
studentSubGroups = dict()
for i in range(1,sheet.nrows):
    g = sheet.cell_value(i,2)
    
    if sheet.cell_type(i,3) == xlrd.XL_CELL_EMPTY:
        sg = g
        studentSubGroups[g] = sg
        continue
    
    subg = sheet.cell_value(i,3).split(',')
    sg = ''
    for s in subg:
        sg = sg+s[0:5]+','
    sg = sg[0:-1]
    studentSubGroups[g] = sg
    
import pickle
with open('studentSubGroups.pickle', 'wb') as f:
    pickle.dump(studentSubGroups, f)

      
#-----------------------------------------------------------------

with open('studentGroups.pickle', 'wb') as f:
    pickle.dump(studentGroups, f)


studentsListXML = '<Students_List>\n'
for si in studentGroups:
    studentsListXML = studentsListXML + '<Year>\n' 
    studentsListXML = studentsListXML + '\t<Name>'+si+'</Name>\n'
    studentsListXML = studentsListXML + '\t<Number_of_Students>'+str(len(studentGroups[si]))+'</Number_of_Students>\n'
    studentsListXML = studentsListXML + '\t<Comments></Comments>\n' 
    
    for gr in sorted(studentGroups[si]):
        studentsListXML = studentsListXML + '\t<Group>\n'
        studentsListXML = studentsListXML + '\t\t<Name>'+gr+'</Name>\n'
        studentsListXML = studentsListXML + '\t\t<Number_of_Students>1</Number_of_Students>\n'
        studentsListXML = studentsListXML + '\t\t<Comments></Comments>\n'
        studentsListXML = studentsListXML + '\t</Group>\n'
    studentsListXML = studentsListXML + '</Year>\n'
studentsListXML = studentsListXML + '</Students_List>\n'

