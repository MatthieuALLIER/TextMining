# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 13:42:01 2022

@author: rpons
"""

import os, pandas as pd
import importTemp

disney = importTemp.disney
compos_clean = importTemp.compos_clean

#  Transformation en liste de texte
compos_clean = [" ".join(w)for w in compos_clean]

# Importer la classe CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
parseur = CountVectorizer()

#pour la colonne "pourquoi"
X = parseur.fit_transform(compos_clean)

# Matrice documents termes
mdt = X.toarray()
print(type(mdt))
print(mdt.shape)

# Ajout des dates
date_sejour = disney["Date séjour"].tolist()

# Parseur date 

import dateparser 
date_sejour=[dateparser.parse(date) for date in date_sejour]
annee=[date.year for date in date_sejour]
mois=[date.month for date in date_sejour]

mdtDF = pd.DataFrame(mdt, columns=parseur.get_feature_names())
mdtSumYear = mdtDF.groupby(annee).sum().transpose()