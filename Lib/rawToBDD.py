# -*- coding: utf-8 -*-
"""
Transforme les données brutes en données à intégrer dans le modèle en étoile
"""
import pandas as pd


def StarToSQLInsert(disney, date, hotel, pays):
    """
    creer le code sql des nouveaux individus
    """
    disney = disney.fillna("Inconnu")
    disney.Positif = [emoji.replace_emoji(text) for text in disney.Positif]
    disney.Titre = [emoji.replace_emoji(text) for text in disney.Titre]
    disney.Négatif = [emoji.replace_emoji(text) for text in disney.Négatif]
    
    query = "INSERT INTO disney VALUES "
    for index, row in disney.iterrows():
        
        #Add modality if not exist
        if row["Date séjour"] not in date.date.tolist():
            date, queryDate = AddModaliteDimension(row["Date séjour"], date, "date")
            pushToBDD(queryDate)
        if row["Pays"] not in pays.pays.tolist():
            pays, queryPays = AddModaliteDimension(row["Pays"], pays, "pays")
            pushToBDD(queryPays)
        
        #Insert row
        query += "('"+row["Prenom"]+"',"+str(row["Note"])+","
        query += str(int(pays[pays["pays"]==row["Pays"]]["id_pays"]))+",'"
        query += str(row["Titre"])+"','"+str(row["Positif"])+"','"+str(row["Négatif"])+"',"
        query += str(int(date[date["date"]==row["Date séjour"]]["id_date"]))+",'"
        query += row["Date commentaire"]+"',"
        query += str(int(hotel[hotel["hotel"]==row["hotel"]]["id_hotel"]))+"),"
    
    query = query[:-1]
        
    return query
        
    
def AddModaliteDimension(modalite, table, dimension):
    """
    ajoute une modalite a la table de dimension concerne
    """
    col_id = table.columns[1]
    id_modalite = max(table.iloc[:,1]) + 1
    table = table.append({dimension:modalite, col_id:id_modalite}, ignore_index=True)
    query = "INSERT INTO "+dimension+" VALUES ('"+modalite+"',"+str(id_modalite)+")"
    
    return table, query


def pushToBDD(query):
    
    