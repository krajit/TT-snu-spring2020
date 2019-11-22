#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 02:14:28 2019

@author: ajit
"""

# importing csv module 
import csv 

with open('csv/snu-timetable/snu-timetable_activities.csv', 'r') as ff:
  reader = csv.reader(ff)
  activities = list(reader)
 
activitiesTime = dict()  
  
i = 0

consXML = ""

for a in activities[1:]:
    if "Lunch" in a[1]:
        continue
    subActivities = a[5].split("+")
    k = len(subActivities)
    if (k > 1):
        ciConstraint = "<ConstraintActivitiesSameStartingHour>\n\t\
<Weight_Percentage>100</Weight_Percentage>\n\t\
<Number_of_Activities>"+str(k)+"</Number_of_Activities>\n"
        for j in range(1,k+1):
            i = i + 1
            ciConstraint = ciConstraint + "\t\t<Activity_Id>"+str(i)+"</Activity_Id>\n"
        ciConstraint = ciConstraint + "\t<Active>true</Active>\n\t\
<Comments></Comments>\n\
</ConstraintActivitiesSameStartingHour>\n"
        consXML = consXML + ciConstraint
    else:
        i = i + k
        
        

f = open("lecDiffDaysSameHourConst.fet",'w+')
f.write(consXML)
f.close

    
    
    
    
#    if a[0] not in activitiesTime:
#        activitiesTime[a[0]] = dict()
#        activitiesTime[a[0]][a[1]] = []
#        activitiesTime[a[0]][a[1]].append(a[2])
#    elif a[1] not in activitiesTime[a[0]]:
#        activitiesTime[a[0]][a[1]] = []
#        activitiesTime[a[0]][a[1]].append(a[2])
#    else:
#        activitiesTime[a[0]][a[1]].append(a[2])
