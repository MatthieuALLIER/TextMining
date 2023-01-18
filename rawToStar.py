# -*- coding: utf-8 -*-
"""
Transforme les données brutes en données à intégrer dans le modèle en étoile
"""
import pandas as pd

def rawToStar(disneyDF):

    """
    recup les id des modalites
    """

    disneyDF = disneyDF.replace(list_pays, id_pays)

    disneyDF = disneyDF.replace(list_hotel, id_hotel)

    disneyDF = disneyDF.replace(list_date, id_date)
    
    return {"disney":disneyDF,"pays":pays,"hotel":hotel,"date":date}

def StarToSQLInsert(disney, date, hotel, pays):
    """
    creer le code sql des nouveaux individus
    """
    query = "INSERT INTO disney VALUES "
    for index, row in disney.iterrows():
        
        #Add modality if not exist
        if row["Date séjour"] not in date.date.tolist():
            AddModaliteDimension(row["Date séjour"], date)
        if row["Hotel"] not in hotel.hotel.tolist():
            AddModaliteDimension(row["Hotel"], hotel)
        if row["Pays"] not in pays.pays.tolist():
            AddModaliteDimension(row["Pays"], pays)
        
        #Insert row
        query += "('"+row["Prenom"]+"',"+str(row["Note"])+","
        query += str(int(pays[pays["pays"]==row["Pays"]]["id_pays"]))+",'"
        query += str(row["Titre"])+"','"+str(row["Positif"])+"','"+str(row["Négatif"])+"',"
        query += str(int(date[date["date"]==row["Date séjour"]]["id_date"]))+",'"
        query += row["Date commentaire"]+"',"
        query += str(int(hotel[hotel["hotel"]==row["Hotel"]]["id_hotel"]))+"),"
        
        #Suppr la dernière ","
        
    
def AddModaliteDimension(modalite, dimension):
    """
    ajoute une modalite a la table de dimension concerne
    """    