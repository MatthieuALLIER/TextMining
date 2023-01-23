# -*- coding: utf-8 -*-
"""

"""
############################################################################################################################################
#                                                                                                                                          # 
#                                                   IMPORT DE LIBRAIRIES                                                                   #
#                                                                                                                                          #
############################################################################################################################################

import pandas as pd
import nltk
import numpy
import string
import matplotlib.pyplot as plt
import dateparser

from analyse_date import analyseDate
from Analyse_pays import analysePays
from analyse_hotel import analyseHotel
from Lib import nettoyage

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

#Importation df pour test
disney = pd.read_csv("data/disney.csv") 
df = disney
############################################################################################################################################
#                                                                                                                                          # 
#  FONCTIONS CREATION "SOUS" DATA FRAME ET CORPUS SELON FILTRES SUR pays, note, hotel, date_sejour, date_commentaire, positif, negatif     #
#                                                                                                                                          #
############################################################################################################################################

# /!\ Pas encore de filtre sur la date /!\

def filtre_df(df, l_pays=df.Pays.unique(), l_note=df.Note.unique(), l_hotel=df.hotel.unique()):
    df_filtered = df[df['Pays'].isin(l_pays) & df['Note'].isin(['l_note']) & df['hotel'].isin(l_hotel)]
    return df_filtered

#Print 3 lignes au hasard
#print(new_df.iloc[random.sample(range(len(new_df)), 3)])

# EXEMPLE
#filtre_pays = ['France','Espagne']
#filtre_df(df=disney, l_pays=filtre_pays)


#Chosir de faire un corpus avec avis positif, negatif ou les deux 
def corpus_pn(df, pos=True, neg=True):
    if ((not pos) & (not neg)) :
        raise ValueError("Vous devez choisir au moins un type de commentaire à afficher") 
    elif (not pos) :
        corpus = df.Négatif.astype(str).tolist()
    elif (not neg) :
        corpus = df.Positif.astype(str).tolist()
    else :
        corpus = df.apply(lambda row: row['Positif'] +' '+ row['Négatif'], axis=1).tolist()
    return corpus
              

############################################################################################################################################
#                                                                                                                                          # 
#                                           FONCTIONS NETTOYAGE POUR ANALYSE TEXTE                                                        #
#                                                                                                                                          #
############################################################################################################################################

def nettoyage_doc(doc_param):
    #initialisation paramètres nettoyage
    mots_vides = stopwords.words('english') + stopwords.words('french')
    new_stopwords = ["🤣🤣👍👍👍","👍👍👍","👍","😡😡😡😡😡😡","😡😡😡😡😡je","arrivé👍","génial👍","disneyland","disney","Disney", 'nan', '😔','très','tout','tous']
    mots_vides.extend(new_stopwords)
    lem = WordNetLemmatizer()
    ponctuations = list(string.punctuation)
    chiffres = list("0123456789")
    #passage en minuscule
    doc = doc_param.lower()
    #retrait des ponctuations
    doc = "".join([w for w in list(doc) if not w in ponctuations])
    #retirer les chiffres
    doc = "".join([w for w in list(doc) if not w in chiffres])
    #transformer le document en liste de termes par tokénisation
    doc = word_tokenize(doc)
    #lematisation de chaque terme
    doc = [lem.lemmatize(terme) for terme in doc]
    #retirer les stopwords
    doc = [w for w in doc if not w in mots_vides]
    #retirer les termes de moins de 3 caractères
    doc = [w for w in doc if len(w)>=3]
    #fin
    return doc

def nettoyage_corpus(corpus,vire_vide=True):
    #output
    output = [nettoyage_doc(doc) for doc in corpus if ((len(doc) > 3) or (vire_vide == False))]
    return output


############################################################################################################################################
#                                                                                                                                          # 
#                                           FONCTIONS CREATION MODELE / DICO + VERIF MOT                                                   #
#                                                                                                                                          #
############################################################################################################################################

def cr_modele(corpus, positif=True, negatif=True) :
    modele = Word2Vec(corpus,vector_size=2,window=3,min_count=1)
    dico = modele.wv
    return dico

#vérifie si le mot tapé est dans le dico et son occurence si oui
def verif_mot(corpus, dico, mot) :
    if (not mot in dico.key_to_index.keys()) :
        print('le mot ' + mot + ' n\'apparait pas dans les commentaires')
    else :
        text = " ".join([" ".join(ligne) for ligne in corpus])
        print('le mot ' +  mot + ' apparait {}'.format(text.split().count(mot)) + ' fois dans les commentaires')
        

############################################################################################################################################
#                                                                                                                                          # 
#                                                     FONCTION ASSOCIATION MOTS                                                            #
#                                                                                                                                          #
############################################################################################################################################

def mots_similaires(dico, liste_mots, n_proches=10):
    return dico.most_similar(liste_mots, topn=n_proches)
    

############################################################################################################################################
#                                                                                                                                          # 
#                                                FONCTION GRAPHIQUE ASSOCIATION MOTS                                                       #
#                                                                                                                                          #
############################################################################################################################################
    
def graph_association(dico, liste_mots):
    df = pd.DataFrame(dico.vectors,columns=['V1','V2'],index=dico.key_to_index.keys())
    dfListe = df.loc[liste_mots,:]

    #graphique dans le plan
    plt.scatter(dfListe.V1,dfListe.V2,s=0.5)
    for i in range(dfListe.shape[0]):
        plt.annotate(dfListe.index[i],(dfListe.V1[i],dfListe.V2[i]))
    plt.show()

# EXEMPLE
# graph_association(dico, ['séjour','personnel','prix','bien','super','cher'])
    
############################################################################################################################################
#                                                                                                                                          # 
#                                       FONCTION GRAPHIQUE DENDOGRAMME + CLUSTER DE MOTS                                                   #
#                                                                                                                                          #
############################################################################################################################################        
#fonction pour transformer un document en vecteur
#à partir des tokens qui le composent
#entrée : doc à traiter
#         modèle entrainé ou préentrainé
#sortie : vecteur représentant le document
def my_doc_2_vec(doc,trained):
    #dimension de représentation
    p = trained.vectors.shape[1]
    #initialiser le vecteur
    vec = numpy.zeros(p)
    #nombre de tokens trouvés
    nb = 0
    #traitement de chaque token du document
    for tk in doc:
        #ne traiter que les tokens reconnus
        if ((tk in trained.key_to_index.keys()) == True):
            values = trained[tk]
            vec = vec + values
            nb = nb + 1.0
    #faire la moyenne des valeurs
    #uniquement si on a trouvé des tokens reconnus bien sûr
    if (nb > 0.0):
        vec = vec/nb
    #renvoyer le vecteur
    #si aucun token trouvé, on a un vecteur de valeurs nulles
    return vec


#fonction pour représenter un corpus à partir d'une représentation
#soit entraînée, soit pré-entraînée
#sortie : représentation matricielle
def my_corpora_2_vec(corpora,trained):
    docsVec = list()
    #pour chaque document du corpus nettoyé
    for doc in corpora:
        #calcul de son vecteur
        vec = my_doc_2_vec(doc,trained)
        #ajouter dans la liste
        docsVec.append(vec)
    #transformer en matrice numpy
    matVec = numpy.array(docsVec)
    return matVec

#CAH à partir de scipy
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster

#pour transformation en MDT
from sklearn.feature_extraction.text import CountVectorizer


#fonction pour construire une typologie à partir
#d'une représentation des termes, qu'elle soit entraînée ou pré-entraînée
#seuil par défaut = 1, mais le but est d'avoir 4 groupes
#corpus ici se présente sous la forme d'une liste de listes de tokens
def my_cah_from_doc2vec(corpus,trained,seuil=1.0,nbTermes=7):

    #matrice doc2vec pour la représentation à 100 dim.
    #entraînée via word2vec sur les documents du corpus
    mat = my_corpora_2_vec(corpus,trained)

    #dimension
    #mat.shape

    #générer la matrice des liens
    Z = linkage(mat,method='ward',metric='euclidean')

    #affichage du dendrogramme
    plt.title("CAH")
    dendrogram(Z,orientation='left',color_threshold=0)
    plt.show()

    #affichage du dendrogramme avec le seuil
    plt.title("CAH")
    dendrogram(Z,orientation='left',color_threshold=seuil)
    plt.show()

    #découpage en 4 classes
    grCAH = fcluster(Z,t=seuil,criterion='distance')
    #print(grCAH)

    #comptage
    print(numpy.unique(grCAH,return_counts=True))

    #***************************
    #interprétation des clusters
    #***************************
    
    #parseur
    parseur = CountVectorizer(binary=True)
    
    #former corpus sous forme de liste de chaîne
    corpus_string = [" ".join(doc) for doc in corpus]
    
    #matrice MDT
    mdt = parseur.fit_transform(corpus_string).toarray()
    print("Dim. matrice documents-termes = {}".format(mdt.shape))
    
    #passer en revue les groupes
    res_cluster = ""
    
    for num_cluster in range(numpy.max(grCAH)):
        res_cluster += "\n"
        #numéro du cluster à traiter
        res_cluster += "Numero du cluster = " + str(num_cluster+1)+"\n"
        groupe = numpy.where(grCAH==num_cluster+1,1,0)
        effectifs = numpy.unique(groupe,return_counts=True)
        res_cluster += "Effectifs = " + str(effectifs[1][1])+"\n"
        #calcul de co-occurence
        cooc = numpy.apply_along_axis(func1d=lambda x: numpy.sum(x*groupe),axis=0,arr=mdt)
        #print(cooc)
        #création d'un data frame intermédiaire
        tmpDF = pd.DataFrame(data=cooc,columns=['freq'],index=parseur.get_feature_names_out())    
        #affichage des "nbTermes" termes les plus fréquents
        res_cluster += str(tmpDF.sort_values(by='freq',ascending=False).iloc[:nbTermes,:])+"\n"
        
    #renvoyer l'indicateur d'appartenance aux groupes
    return grCAH, mat, res_cluster

#*** fin de la fonction


#EXEMPLE D'APPEL DE LA FONCTION
#g1,mat1 = my_cah_from_doc2vec(corpus,dico,seuil=10)

def preparation(disney):
    # Passage de la colonne date_sejour en format date
    print("Formatage des dates...")
     
    date_sejour = disney["Date séjour"].tolist()
    date_sejour=[dateparser.parse(date) for date in date_sejour]
    global annee
    annee=[date.year for date in date_sejour]
    
    # Sélection des pays
    print("Sélection des pays")
    # On crée une une liste contenant la liste des pays sans doublons 
    global liste_pays
    liste_pays = list(set(disney["Pays"]))
    
    # On choisis uniquement les pays avec plus de 200 commentaires
    liste_pays = [pays for pays in liste_pays if len(disney[disney.Pays == pays])>=200]
    
    #Index de avis de ces pays
    index_ind_pays = [i for i in range(len(disney)) if disney.Pays[i] in liste_pays]

    titre, indexTitre = nettoyage.nettoyageColAvis(disney,"Titre")
    positif, indexPositif = nettoyage.nettoyageColAvis(disney,"Positif")
    negatif, indexNegatif = nettoyage.nettoyageColAvis(disney,"Négatif")
    
    indexTitrePays = set(indexTitre).intersection(index_ind_pays)
    indexPositifPays = set(indexPositif).intersection(index_ind_pays)
    indexNegatifPays = set(indexNegatif).intersection(index_ind_pays)
    
    titreDate = analyseDate(titre, annee, indexTitre, "titre")
    titreHotel = analyseHotel(titre, disney.hotel, indexTitre, "titre")
    titrePays = analysePays([disney["Titre"][i] for i in indexTitrePays], disney.Pays, indexTitrePays, "titre")
    positifDate = analyseDate(positif, annee, indexPositif, "positif")
    positifHotel = analyseHotel(positif, disney.hotel, indexPositif, "positif")
    positifPays = analysePays([disney["Positif"][i] for i in indexPositifPays], disney.Pays, indexPositifPays, "positif")
    negatifDate = analyseDate(negatif, annee, indexNegatif, "négatif")
    negatifHotel = analyseHotel(negatif, disney.hotel, indexNegatif, "négatif")
    negatifPays = analysePays([disney["Négatif"][i] for i in indexNegatifPays], disney.Pays, indexNegatifPays, "négatif")
    
    nbAvis = len(disney)
    nbGood = len(disney[disney.Positif != "Inconnu"])
    nbBad = len(disney[disney.Négatif != "Inconnu"])
    noteAvg = round(disney.Note.mean(), 2)
    noteMin = min(disney.Note)
    noteMax = max(disney.Note)
    dateMin = min(annee)
    dateMax = max(annee)
    nbPays = len(list(set(disney["Pays"])))
    nbPays200 = len(liste_pays)
    
    return {"titreDate":titreDate,"titreHotel":titreHotel,"titrePays":titrePays,
            "positifDate":positifDate,"positifHotel":positifHotel,"positifPays":positifPays,
            "negatifDate":negatifDate,"negatifHotel":negatifHotel,"negatifPays":negatifPays,
            "nbAvis":nbAvis,"nbGood":nbGood,"nbBad":nbBad,
            "noteAvg":noteAvg,"noteMin":noteMin,"noteMax":noteMax,
            "dateMin":dateMin,"dateMax":dateMax,
            "nbPays":nbPays,"nbPays200":nbPays200,
            "annee":annee,"liste_pays":liste_pays} 



























