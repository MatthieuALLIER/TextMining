# -*- coding: utf-8 -*-
"""

"""
import os, pandas as pd
# DFnames = ["cheyenne", "newYork", "newportBay", "sequoiaLodge", "santaFe", "davyCrockettRanch"]

# #Importation from csv
# disney = pd.DataFrame(columns = ["Prenom","Note","Pays","Titre","Positif","Négatif","Date séjour","Date commentaire","hotel"])
# for i in range(len(DFnames)): 
#     nameDF = DFnames[i]
#     DF = pd.read_csv("./data/"+nameDF+".csv", index_col=0)  
#     DF["hotel"] = nameDF
#     disney = pd.concat([disney, DF])
#     globals()[nameDF] = DF


disney = pd.read_csv("data/disney.csv")


# On crée une une liste contenant la liste des pays sans doublons 
liste_pays = disney["Pays"]
liste_pays_unique = []
for pays in liste_pays:
    if pays not in liste_pays_unique:
        liste_pays_unique.append(pays)


# On sépare les pays en comptant le nombre de commentaire
cinq_commentaires_ou_moins = []
plus_cinq_commentaires = []
test = disney[disney.Pays == "Honduras"]

for pays in liste_pays_unique :
    if len(disney[disney.Pays == pays])<=200:
        cinq_commentaires_ou_moins.append(pays)
    else:
        plus_cinq_commentaires.append(pays)

disney_bis = disney[disney.Pays.isin(plus_cinq_commentaires)]

print(disney_bis.Pays.value_counts())
#Analyses
from Lib import nettoyage

corpusTitre = disney_bis.Titre.tolist()
disney_bis.Titre = corpusTitre

corpuspos = disney_bis.Positif.tolist()
disney_bis.Positif = corpuspos

corpusneg = disney_bis.Négatif.tolist()
disney_bis.Négatif = corpusneg


#nettoyage des nan
corpusTitre = [str(i) for i in corpusTitre]

#Suppression des titres par défaut
listTitreDefaut = ["Mauvais","Médiocre","Assez médiocre", "Décevant", "Passable",
                   "Agréable", "Bien", "Très bien", "Fabuleux", "Exceptionnel", "nan"]
corpusTitre = [i for i in corpusTitre if not i in listTitreDefaut]

#Nettoyage global du corpus
corpusTitre = nettoyage.nettoyage_corpus(corpusTitre)

