# -*- coding: utf-8 -*-
"""

"""
import os, pandas as pd
DFnames = ["cheyenne", "newYork", "newportBay", "sequoiaLodge", "santaFe", "davyCrockettRanch"]

#Importation from csv
disney = pd.DataFrame(columns = ["Prenom","Note","Pays","Titre","Positif","Négatif","Date séjour","Date commentaire","hotel"])
for i in range(len(DFnames)): 
    nameDF = DFnames[i]
    DF = pd.read_csv("./data/"+nameDF+".csv", index_col=0)  
    DF["hotel"] = nameDF
    disney = pd.concat([disney, DF])
    globals()[nameDF] = DF

#Analyses
from nettoyage import nettoyage_corpus

#Filtre en attendant
disney = disney[disney.Pays == "France"]
disney = disney[disney.Positif != "Ce client n'a pas laissé de commentaire."]

# Passage des commentaires en liste
compos=disney.Positif.tolist()

# Nettoyage 
compos_clean = [str(i) for i in compos]
compos_clean=nettoyage_corpus(compos_clean)

