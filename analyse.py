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

#Filtre france en attendant
disney = disney[disney.Pays == "France"]
corpusTitre = disney.Titre.tolist()

#nettoyage des nan
corpusTitre = [str(i) for i in corpusTitre]

#Suppression des titres par défaut
listTitreDefaut = ["Mauvais","Médiocre","Assez médiocre", "Décevant", "Passable",
                   "Agréable", "Bien", "Très bien", "Fabuleux", "Exceptionnel"]
corpusTitre = [i for i in corpusTitre if not i in listTitreDefaut]

#Nettoyage global du corpus
corpusTitre = nettoyage_corpus(corpusTitre)

from gensim.models import Word2Vec
modele = Word2Vec(corpusTitre,vector_size=2,window=3,min_count=1)

#propriété "wv" -> wordvector
words = modele.wv


