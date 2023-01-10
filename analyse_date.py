# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 13:42:01 2022

@author: rpons
"""

import pandas as pd, numpy as np
import importTemp

from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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

castle_mask = np.array(Image.open("data/disneyCastle.png"))
compos_array = np.array(compos_clean)

for an in list(set(annee)):
    wc = WordCloud(background_color="black", max_words=2000, mask=castle_mask, 
                   contour_width=3, width=200, height=300, colormap="gist_rainbow")
    
    index = [i for i in range(len(annee)) if annee[i] == an]
    
    wc.generate(" ".join(compos_array[index]))
    
    plt.figure(figsize=(10,15))
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig("out/CastleWC_"+str(an)+".png")



















