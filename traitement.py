# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 11:32:28 2022

@author: mallier
"""

namesClean = userNames

notesClean = []
for i in notes:
    if type(i)==str:
        notesClean.append(float(i.replace(" ","").replace(",",".")))
    else:
        notesClean.append(None)

countryClean = []
for i in country:
    if type(i)==str:
        countryClean.append(i[2:])
    else:
        countryClean.append(None)
        
titlesClean = []
for i in titles:
    if type(i)==str:
        titlesClean.append(i.split("\n")[1].split("\xa0")[0])
    else:
        titlesClean.append(None)
        
posComsClean = []
for i in posComs:
    if type(i)==str:
        posComsClean.append(i.replace("\n", " "))
    else:
        posComsClean.append(None)
        

posNegClean = []
for i in posNeg:
    if type(i)==str:
        posNegClean.append(i.replace("\n", " "))
    else:
        posNegClean.append(None)
        
travelDate
comDate