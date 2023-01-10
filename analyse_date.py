# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 13:42:01 2022

@author: rpons
"""

import os, pandas as pd, numpy as np
import matplotlib.pyplot as plt
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

from PIL import Image
castle_mask = np.array(Image.open("data/disneyCastle.png"))

from wordcloud import WordCloud
wc = WordCloud(background_color="black", max_words=2000, mask=castle_mask, 
               contour_width=3, width=200, height=300, colormap="gist_rainbow")

wc.generate(" ".join(compos_clean))

import matplotlib.pyplot as plt
plt.figure(figsize=(10,15))
plt.imshow(wc)
plt.axis("off")
plt.savefig("out/CastleWC.png")



















