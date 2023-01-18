# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:19:23 2023

@author: Asus
"""

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