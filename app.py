# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

import pandas as pd

import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from wordcloud import WordCloud
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from datetime import date

from Lib import nettoyage, loopScraping, scrapping, rawToBDD, traduction
from analyse_date import analyseDate
from Analyse_pays import analysePays
from analyse_hotel import analyseHotel

import mysql.connector
from mysql.connector import Error

#Connection à la Base de donnée
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='disney_avis_booking',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connecté à MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("Vous êtes connecté à la base : ", record)

except Error as e:
    print("Error while connecting to MySQL", e)

#Importation des données
disney = rawToBDD.reqToBDD(connection, "SELECT * FROM disney", "select")
disney = pd.DataFrame(disney, columns=['Prenom', 'Note', 'Pays', 'Titre', 'Positif',
                                       'Négatif', 'Date séjour', 'Date commentaire',
                                       'hotel'])

date = rawToBDD.reqToBDD(connection, "SELECT * FROM date", "select")
date = pd.DataFrame(date, columns=['date', 'id_date'])

hotel = rawToBDD.reqToBDD(connection, "SELECT * FROM hotel", "select")
hotel = pd.DataFrame(hotel, columns=['hotel', 'id_hotel'])

pays = rawToBDD.reqToBDD(connection, "SELECT * FROM pays", "select")
pays = pd.DataFrame(pays, columns=['pays', 'id_pays'])

#Jointure en mode replace
disney["Date séjour"] = disney["Date séjour"].replace(list(date.id_date), list(date.date))
disney["hotel"] = disney["hotel"].replace(list(hotel.id_hotel), list(hotel.hotel))
disney["Pays"] = disney["Pays"].replace(list(pays.id_pays), list(pays.pays))
disney.Note = pd.to_numeric(disney.Note)

#KPIs
nbAvis = len(disney)
nbGood = len(disney[disney.Positif != "Inconnu"])
nbBad = len(disney[disney.Négatif != "Inconnu"])
noteAvg = round(disney.Note.mean(), 2)
noteMin = min(disney.Note)
noteMax = max(disney.Note)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Disney textmining')
server = app.server

# # # Passage de la colonne date_sejour en format date
# print("Formatage des dates")
# import dateparser 
# date_sejour = disney["Date séjour"].tolist()
# date_sejour=[dateparser.parse(date) for date in date_sejour]
# annee=[date.year for date in date_sejour]


# # Sélection des pays
# # On crée une une liste contenant la liste des pays sans doublons 
# liste_pays = disney["Pays"]
# liste_pays_unique = []
# for pays in liste_pays:
#     if pays not in liste_pays_unique:
#         liste_pays_unique.append(pays)

# # On choisis uniquement les pays avec plus de 200 commentaires
# liste_pays = []
# for pays in liste_pays_unique :
#     if len(disney[disney.Pays == pays])>=200:
#         liste_pays.append(pays)


# index_pays = [i for i in range(len(disney)) if disney.Pays[i] in liste_pays]

# # #### Nettoyage
# # Titre
# print("Nettoyage des titres")
# # On enlève les inconnus dans les avis
# titre=nettoyage.nettoyage_corpus(disney.Titre)
# titre_join = [" ".join(w)for w in titre]
# # On enlève les inconnus dans les avis
# index=[i for i in range(len(titre_join)) if titre_join[i] != "inconnu"]
# titre_join = [titre_join[i] for i in index]


# # Fonction d'analyse par année pour les titres
# titredate=analyseDate(titre_join,annee,index,"titre")

# # Fonction d'analyse par hotel pour les titres
# titrehotel = analyseHotel(titre_join,disney.hotel,index,"titre")



# # Analyse par pays
# index_bis = [index[i] for i in range(0,len(index)-1) if index[i] in index_pays]
# titre_join_bis = [" ".join(w)for w in titre]
# titre_join_bis = [titre_join_bis[i] for i in index_bis]
# titrepays=analysePays(titre_join_bis,disney.Pays,index_bis,"titre")

# # Commentairs positifs
# print("Nettoyage des commentaires positifs")
# positif=nettoyage.nettoyage_corpus(disney.Positif)
# positif_join = [" ".join(w)for w in positif]
# # On enlève les inconnus dans les avis
# index=[i for i in range(len(positif_join)) if positif_join[i] != "inconnu"]
# positif_join = [positif_join[i] for i in index]

# # Fonction d'analyse par année pour les commentaires positifs
# posdate=analyseDate(positif_join,annee,index,"positif")

# # Fonction d'analyse par hotel pour les positifs
# poshotel = analyseHotel(positif_join,disney.hotel,index,"positif")

# # Analyse par pays
# index_bis = [index[i] for i in range(0,len(index)-1) if index[i] in index_pays]
# positif_join_bis = [" ".join(w)for w in positif]
# positif_join_bis = [positif_join_bis[i] for i in index_bis]
# pospays=analysePays(positif_join_bis,disney.Pays,index_bis,"positif")

# # Commentaires négatifs
# print("Nettoyage des commentaires négatifs")
# negatif=nettoyage.nettoyage_corpus(disney.Négatif)
# negatif_join = [" ".join(w)for w in negatif]
# # On enlève les inconnus dans les avis
# index=[i for i in range(len(negatif_join)) if negatif_join[i] != "inconnu"]
# negatif_join = [negatif_join[i] for i in index]

# # Fonction d'analyse par année pour les commentaires négatifs
# negdate=analyseDate(negatif_join,annee,index,"négatif")


# # Fonction d'analyse par hotel pour les négatifs
# neghotel = analyseHotel(negatif_join,disney.hotel,index,"négatif")


# # Analyse par pays
# index_bis = [index[i] for i in range(0,len(index)-1) if index[i] in index_pays]
# negatif_join_bis = [" ".join(w)for w in negatif]
# negatif_join_bis = [negatif_join_bis[i] for i in index_bis]
# negpays=analysePays(negatif_join_bis,disney.Pays,index_bis,"négatif")


#Menu
TABPANEL = dbc.Container([
    html.H2("Analyse des commentaires Disney"),
    html.H3("Source : Booking.com"),
    html.Hr(),
    dbc.Tabs(
        [
            dbc.Tab(label="Accueil", tab_id="index"),
            dbc.Tab(label="Données", tab_id="data"),
            dbc.Tab(label="Analyse", tab_id="analyse")           
        ],
        id="tabPanel",
        active_tab="index",
    )
])

#Content
PageContent = dbc.Container([
    dcc.Store("disney"),
    html.Div([
        #Accueil
        html.P("Accueil")
    ], id="index-tab", style= {'display': 'block'}),
    html.Div([
        dbc.Tabs([
                    dbc.Tab(label="KPIs", tab_id="kpi"),
                    dbc.Tab(label="Acquisition", tab_id="getData")     
                ], id="tabPanelData", active_tab="kpi"),
        html.Div([
            #KPIs
            html.P("KPIs")
        ], id="kpi-tab", style= {'display': 'none'}),
        html.Div([
            html.Button('Mettre à jour', id='MAJ'),
        ], id="getData-tab", style= {'display': 'none'})
        
    ], id="data-tab", style= {'display': 'none'}),
    html.Div([
        dbc.Tabs([
                    dbc.Tab(label="Date", tab_id="date"),
                    dbc.Tab(label="Pays", tab_id="pays"),
                    dbc.Tab(label="Hôtel", tab_id="hotel"),
                    dbc.Tab(label="Mots liés", tab_id="lies")    
                ], id="tabPanelAnalyse", active_tab="date"),
        html.Div([
            #Date
            # dcc.DatePickerRange(
            #     display_format='M/Y',
            #     start_date=min(date_sejour),
            #     end_date=max(date_sejour)
            #  )
            dcc.Dropdown(
                   options={"1":'Titre', "2":'Commentaires positifs', "3":'Commentaires négatifs'},
                   value="1",
                   style={'color': 'Pink', 'font-size': 20},
                   clearable = False,
                   id="liste_choix_corpus_date"
             ),
            html.Div([
               html.Img(src=r"assets/titre/CastleWC_2019.png",width='20%'),
               html.Img(src=r"assets/titre/CastleWC_2020.png",width='20%'),
               html.Img(src=r"assets/titre/CastleWC_2021.png",width='20%'),
               html.Img(src=r"assets/titre/CastleWC_2022.png",width='20%'),
               html.Img(src=r"assets/titre/CastleWC_2023.png",width='20%')
            ], id="date-titre", style= {'display': 'none'}),
            
            html.Div([
               html.Img(src=r"assets/positif/CastleWC_2019.png",width='20%'),
               html.Img(src=r"assets/positif/CastleWC_2020.png",width='20%'),
               html.Img(src=r"assets/positif/CastleWC_2021.png",width='20%'),
               html.Img(src=r"assets/positif/CastleWC_2022.png",width='20%'),
               html.Img(src=r"assets/positif/CastleWC_2023.png",width='20%')
            ], id="date-positif", style= {'display': 'none'}),
            
            html.Div([
               html.Img(src=r"assets/négatif/CastleWC_2019.png",width='20%'),
               html.Img(src=r"assets/négatif/CastleWC_2020.png",width='20%'),
               html.Img(src=r"assets/négatif/CastleWC_2021.png",width='20%'),
               html.Img(src=r"assets/négatif/CastleWC_2022.png",width='20%'),
               html.Img(src=r"assets/négatif/CastleWC_2023.png",width='20%')
            ], id="date-negatif", style= {'display': 'none'})
            
        ], id="date-tab", style= {'display': 'none'}),
        html.Div([
            #Pays
            html.P("Pays")
        ], id="pays-tab", style= {'display': 'none'}),
        html.Div([
            #Hôtel
            html.P("Hôtel")
        ], id="hotel-tab", style= {'display': 'none'}),
        html.Div([
            #Mots liés
            html.P("Mots liés")
        ], id="lies-tab", style= {'display': 'none'})
    ], id="analyse-tab", style= {'display': 'none'})
])

#Apparence
app.layout = html.Div([TABPANEL, PageContent])

#Callback
@app.callback([Output('index-tab', 'style'),
               Output('data-tab', 'style'), 
               Output('analyse-tab', 'style')],
               [Input('tabPanel', 'active_tab')])
def tabChange(value):
    if value == "index":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "data":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "analyse":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]
    
@app.callback([Output('kpi-tab', 'style'),
               Output('getData-tab', 'style')],
               [Input('tabPanelData', 'active_tab')])
def tabChangeData(value):
    if value == "kpi":
        return [{'display': 'block'},
                {'display': 'none'}]
    if value == "getData":
        return [{'display': 'none'},
                {'display': 'block'}]
    
@app.callback([Output('date-tab', 'style'),
               Output('pays-tab', 'style'), 
               Output('hotel-tab', 'style'),
               Output('lies-tab', 'style')],
               [Input('tabPanelAnalyse', 'active_tab')])
def tabChangeAnalyse(value):
    if value == "date":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "pays":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "hotel":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "lies":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]
    
@app.callback([Output('date-titre', 'style'),
               Output('date-positif', 'style'),
               Output('date-negatif', 'style')],
               [Input('liste_choix_corpus_date', 'value')])
def DateChangeCorpus(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]
    
@app.callback([Output("disney", "data")],
              [Input('MAJ', 'n_clicks')])
def MiseAJour(n_clicks):
    global disney
    global date
    global hotel
    global pays
    global connection
    if n_clicks is not None:        
        newAvis = loopScraping.loopScraping(disney)
        date, pays = rawToBDD.StarToSQLInsert(newAvis, date, hotel, pays, connection)
        disney = disney.append(newAvis)
        disney.to_csv("data/disney.csv", index=False)  
        
    return [disney.to_dict('records')]

#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
