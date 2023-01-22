# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 19:09:01 2023

@author: spica
"""

import pandas as pd, numpy as np

from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from Lib import nettoyage
import fonctions_analyse as fa

def analyseHotel(compos_clean, hotel, index, type_analyse):
    
    hotel= [hotel[i] for i in index]
    parseur = CountVectorizer()
    
    #pour la colonne "pourquoi"
    X = parseur.fit_transform(compos_clean)
    
    # Matrice documents termes
    mdt = X.toarray()
    print(type(mdt))
    print(mdt.shape)
    
    mdtDF = pd.DataFrame(mdt, columns=parseur.get_feature_names())
    mdtSumhotel = mdtDF.groupby(hotel).sum().transpose()
    
    castle_mask = np.array(Image.open("data/disneyCastle.png"))
    compos_array = np.array(compos_clean)
    
    for an in list(set(hotel)):
        wc = WordCloud(background_color="black", max_words=2000, mask=castle_mask, 
                       contour_width=3, width=200, height=300, colormap="gist_rainbow")
        
        index = [i for i in range(len(hotel)) if hotel[i] == an]
        
        wc.generate(" ".join(compos_array[index]))
        
        plt.figure(figsize=(10,15))
        plt.imshow(wc)
        plt.axis("off")
        plt.savefig("assets/" + str(type_analyse)+ "/CastleWC_"+str(an)+".png")
        
    corpus = []
    for i in range(0,len(compos_clean)):
       corpus.append(nettoyage.nettoyage_doc(compos_clean))
    
    dico = fa.cr_modele(corpus)
    
    sim = fa.mots_similaires(dico, ['séjour','personnel','prix','bien','super','cher'])
    
    fa.graph_association(dico, ['séjour','personnel','prix','bien','super','cher'])
    
    g1,mat1, cluster = fa.my_cah_from_doc2vec(corpus,dico,seuil=10)
    return mdtSumhotel,sim,cluster