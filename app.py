# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

#Utils
import pandas as pd
from datetime import date
import dateparser

#TextMining
from wordcloud import WordCloud

#Dash
import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

#Plotly
import plotly.express as px
import plotly.graph_objects as go

#MySQL
import mysql.connector
from mysql.connector import Error

#Lib interne
from Lib import nettoyage, loopScraping, rawToBDD
from analyse_date import analyseDate
from Analyse_pays import analysePays
from analyse_hotel import analyseHotel
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

def preparation(disney):
    # Passage de la colonne date_sejour en format date
    print("Formatage des dates...")
     
    date_sejour = disney["Date séjour"].tolist()
    date_sejour=[dateparser.parse(date) for date in date_sejour]
    annee=[date.year for date in date_sejour]
    
    
    # Sélection des pays
    print("Sélection des pays")
    # On crée une une liste contenant la liste des pays sans doublons 
    liste_pays = list(set(disney["Pays"]))
    
    # On choisis uniquement les pays avec plus de 200 commentaires
    liste_pays = [pays for pays in liste_pays if len(disney[disney.Pays == pays])>=200]
    
    #Index de avis de ces pays
    index_ind_pays = [i for i in range(len(disney)) if disney.Pays[i] in liste_pays]

    titre, indexTitre = nettoyage.nettoyageColAvis(disney,"Titre")
    positif, indexPositif = nettoyage.nettoyageColAvis(disney,"Positif")
    negatif, indexNegatif = nettoyage.nettoyageColAvis(disney,"Négatif")
    
    indexTitrePays = set(titre).intersection(index_ind_pays)
    indexPositifPays = set(positif).intersection(index_ind_pays)
    indexNegatifPays = set(negatif).intersection(index_ind_pays)
    
    titreDate = analyseDate(titre, annee, indexTitre, "titre")
    titreHotel = analyseHotel(titre, disney.hotel, indexTitre, "titre")
    titrePays = analysePays(titre, disney.Pays, indexTitrePays, "titre")
    positifDate = analyseDate(positif, annee, indexPositif, "positif")
    positifHotel = analyseHotel(positif, disney.hotel, indexPositif, "positif")
    positifPays = analysePays(positif, disney.Pays, indexPositifPays, "positif")
    negatifDate = analyseDate(negatif, annee, indexNegatif, "négatif")
    negatifHotel = analyseHotel(negatif, disney.hotel, indexNegatif, "négatif")
    negatifPays = analysePays(negatif, disney.Pays, indexNegatifPays, "négatif")
    
    #KPIs
    nbAvis = len(disney)
    nbGood = len(disney[disney.Positif != "Inconnu"])
    nbBad = len(disney[disney.Négatif != "Inconnu"])
    noteAvg = round(disney.Note.mean(), 2)
    noteMin = min(disney.Note)
    noteMax = max(disney.Note)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Disney textmining')
server = app.server    

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
    html.Div([], id="no-output", style= {'display': 'none'}),
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
            html.Button('Actualiser les analyses', id='Actu')
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
                   style={'font-size': 20},
                   clearable = False,
                   id="liste_choix_corpus_date"
             ),
            html.Div([
                dcc.Dropdown(
                       options={"1":'2019', "2":'2020', "3":'2021',"4":"2022","5":"2023"},
                       value="1",
                       style={'font-size': 20},
                       clearable = False,
                       id="liste_choix_date_titre"
                 ),
                
                
               html.Img(src=r"assets/titre/CastleWC_2019.png",width='50%', id="titre-2019", style= {'display': 'none'}),
               html.Img(src=r"assets/titre/CastleWC_2020.png",width='50%', id="titre-2020", style= {'display': 'none'}),
               html.Img(src=r"assets/titre/CastleWC_2021.png",width='50%', id="titre-2021", style= {'display': 'none'}),
               html.Img(src=r"assets/titre/CastleWC_2022.png",width='50%', id="titre-2022", style= {'display': 'none'}),
               html.Img(src=r"assets/titre/CastleWC_2023.png",width='50%', id="titre-2023", style= {'display': 'none'})
            ], id="date-titre", style= {'display': 'none'}),
            
            html.Div([
                    dcc.Dropdown(
                           options={"1":'2019', "2":'2020', "3":'2021',"4":"2022","5":"2023"},
                           value="1",
                           style={'font-size': 20},
                           clearable = False,
                           id="liste_choix_date_positif"
                     ),
               html.Img(src=r"assets/positif/CastleWC_2019.png",width='50%',id="positif-2019", style= {'display': 'none'}),
               html.Img(src=r"assets/positif/CastleWC_2020.png",width='50%',id="positif-2020", style= {'display': 'none'}),
               html.Img(src=r"assets/positif/CastleWC_2021.png",width='50%',id="positif-2021", style= {'display': 'none'}),
               html.Img(src=r"assets/positif/CastleWC_2022.png",width='50%',id="positif-2022", style= {'display': 'none'}),
               html.Img(src=r"assets/positif/CastleWC_2023.png",width='50%',id="positif-2023", style= {'display': 'none'})
            ], id="date-positif", style= {'display': 'none'}),
            
            html.Div([
                    dcc.Dropdown(
                           options={"1":'2019', "2":'2020', "3":'2021',"4":"2022","5":"2023"},
                           value="1",
                           style={'font-size': 20},
                           clearable = False,
                           id="liste_choix_date_negatif"
                     ),
               html.Img(src=r"assets/négatif/CastleWC_2019.png",width='50%',id="négatif-2019", style= {'display': 'none'}),
               html.Img(src=r"assets/négatif/CastleWC_2020.png",width='50%',id="négatif-2020", style= {'display': 'none'}),
               html.Img(src=r"assets/négatif/CastleWC_2021.png",width='50%',id="négatif-2021", style= {'display': 'none'}),
               html.Img(src=r"assets/négatif/CastleWC_2022.png",width='50%',id="négatif-2022", style= {'display': 'none'}),
               html.Img(src=r"assets/négatif/CastleWC_2023.png",width='50%',id="négatif-2023", style= {'display': 'none'})
            ], id="date-negatif", style= {'display': 'none'})
            
        ], id="date-tab", style= {'display': 'none'}),
        html.Div([
            #Pays
            dcc.Dropdown(
                       options={"1":'Titre', "2":'Commentaires positifs', "3":'Commentaires négatifs'},
                       value="1",
                       style={'font-size': 20},
                       clearable = False,
                       id="liste_choix_corpus_pays"
                 ),
                

                
                html.Div([
                    dcc.Dropdown(
                           options={"1":'Allemagne', "2":'Belgique', "3":'Espagne', "4":"France", "5":"Italie", "6":"Pays-Bas", "7":"Royaume-Uni","8":"Suisse"},
                           value="1",
                           style={'font-size': 20},
                           clearable = False,
                           id="liste_choix_pays_titre"
                     ),
                    
                   html.Img(src=r"assets/titre/CastleWC_Allemagne.png", width='50%', id="titre-Allemagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Belgique.png",width='50%', id="titre-Belgique", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Espagne.png",width='50%', id="titre-Espagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_France.png",width='50%', id="titre-France", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Italie.png",width='50%', id="titre-Italie", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Pays-Bas.png",width='50%', id="titre-Pays-Bas", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Royaume-Uni.png",width='50%', id="titre-Royaume-Uni", style= {'display': 'none'}),
                   html.Img(src=r"assets/titre/CastleWC_Suisse.png",width='50%', id="titre-Suisse", style= {'display': 'none'})
                ], id="pays-titre", style= {'display': 'none'}),
                
                html.Div([
                    dcc.Dropdown(
                           options={"1":'Allemagne', "2":'Belgique', "3":'Espagne', "4":"France", "5":"Italie", "6":"Pays-Bas", "7":"Royaume-Uni","8":"Suisse"},
                           value="1",
                           style={'font-size': 20},
                           clearable = False,
                           id="liste_choix_pays_positif"
                     ),
                   html.Img(src=r"assets/positif/CastleWC_Allemagne.png", width='50%', id="positif-Allemagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Belgique.png",width='50%', id="positif-Belgique", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Espagne.png",width='50%', id="positif-Espagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_France.png",width='50%', id="positif-France", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Italie.png",width='50%', id="positif-Italie", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Pays-Bas.png",width='50%', id="positif-Pays-Bas", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Royaume-Uni.png",width='50%', id="positif-Royaume-Uni", style= {'display': 'none'}),
                   html.Img(src=r"assets/positif/CastleWC_Suisse.png",width='50%', id="positif-Suisse", style= {'display': 'none'})
                ], id="pays-positif", style= {'display': 'none'}),
                
                html.Div([
                    dcc.Dropdown(
                           options={"1":'Allemagne', "2":'Belgique', "3":'Espagne', "4":"France", "5":"Italie", "6":"Pays-Bas", "7":"Royaume-Uni","8":"Suisse"},
                           value="1",
                           style={'font-size': 20},
                           clearable = False,
                           id="liste_choix_pays_negatif"
                     ),
                     
                   html.Img(src=r"assets/négatif/CastleWC_Allemagne.png", width='50%', id="négatif-Allemagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Belgique.png",width='50%', id="négatif-Belgique", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Espagne.png",width='50%', id="négatif-Espagne", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_France.png",width='50%', id="négatif-France", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Italie.png",width='50%', id="négatif-Italie", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Pays-Bas.png",width='50%', id="négatif-Pays-Bas", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Royaume-Uni.png",width='50%', id="négatif-Royaume-Uni", style= {'display': 'none'}),
                   html.Img(src=r"assets/négatif/CastleWC_Suisse.png",width='50%', id="négatif-Suisse", style= {'display': 'none'})
                ], id="pays-negatif", style= {'display': 'none'})
        ], id="pays-tab", style= {'display': 'none'}),
        html.Div([
            #Hôtel
            dcc.Dropdown(
                    options={"1":'Titre', "2":'Commentaires positifs', "3":'Commentaires négatifs'},
                    value="1",
                    style={'font-size': 20},
                    clearable = False,
                    id="liste_choix_corpus_hotel"
              ),
             html.Div([
                  dcc.Dropdown(
                         options={"1":'Hôtel Cheyenene', "2":'Hôtel Davy Crockett Ranch', "3":'Hôtel NewPort Bay', "4":"Hôtel New York", "5":"Hôtel Santa Fe ", "6":"Hôtel Sequoia Lodge"},
                         value="1",
                         style={'font-size': 20},
                         clearable = False,
                         id="liste_choix_hotel_titre"
                   ),
                html.Img(src=r"assets/titre/CastleWC_cheyenne.png",width='50%',id="titre-cheyenne", style= {'display': 'none'}),
                html.Img(src=r"assets/titre/CastleWC_davyCrockettRanch.png",width='50%',id="titre-davyCrockettRanch", style= {'display': 'none'}),
                html.Img(src=r"assets/titre/CastleWC_newportBay.png",width='50%',id="titre-newportBay", style= {'display': 'none'}),
                html.Img(src=r"assets/titre/CastleWC_newYork.png",width='50%',id="titre-newYork", style= {'display': 'none'}),
                html.Img(src=r"assets/titre/CastleWC_santaFe.png",width='50%',id="titre-santaFe", style= {'display': 'none'}),
                html.Img(src=r"assets/titre/CastleWC_sequoiaLodge.png",width='50%',id="titre-sequoiLodge", style= {'display': 'none'})
             ], id="hotel-titre", style= {'display': 'none'}),
             
             html.Div([
                  dcc.Dropdown(
                         options={"1":'Hôtel Cheyenene', "2":'Hôtel Davy Crockett Ranch', "3":'Hôtel NewPort Bay', "4":"Hôtel New York", "5":"Hôtel Santa Fe ", "6":"Hôtel Sequoia Lodge"},
                         value="1",
                         style={'font-size': 20},
                         clearable = False,
                         id="liste_choix_hotel_positif"
                   ),
                html.Img(src=r"assets/positif/CastleWC_cheyenne.png",width='50%',id="positif-cheyenne", style= {'display': 'none'}),
                html.Img(src=r"assets/positif/CastleWC_davyCrockettRanch.png",width='50%',id="positif-davyCrockettRanch", style= {'display': 'none'}),
                html.Img(src=r"assets/positif/CastleWC_newportBay.png",width='50%',id="positif-newportBay", style= {'display': 'none'}),
                html.Img(src=r"assets/positif/CastleWC_newYork.png",width='50%',id="positif-newYork", style= {'display': 'none'}),
                html.Img(src=r"assets/positif/CastleWC_santaFe.png",width='50%',id="positif-santaFe", style= {'display': 'none'}),
                html.Img(src=r"assets/positif/CastleWC_sequoiaLodge.png",width='50%',id="positif-sequoiLodge", style= {'display': 'none'})
             ], id="hotel-positif", style= {'display': 'none'}),
             
             html.Div([
                  dcc.Dropdown(
                         options={"1":'Hôtel Cheyenene', "2":'Hôtel Davy Crockett Ranch', "3":'Hôtel NewPort Bay', "4":"Hôtel New York", "5":"Hôtel Santa Fe ", "6":"Hôtel Sequoia Lodge"},
                         value="1",
                         style={'font-size': 20},
                         clearable = False,
                         id="liste_choix_hotel_negatif"
                   ),
                html.Img(src=r"assets/négatif/CastleWC_cheyenne.png",width='50%',id="négatif-cheyenne", style= {'display': 'none'}),
                html.Img(src=r"assets/négatif/CastleWC_davyCrockettRanch.png",width='50%',id="négatif-davyCrockettRanch", style= {'display': 'none'}),
                html.Img(src=r"assets/négatif/CastleWC_newportBay.png",width='50%',id="négatif-newportBay", style= {'display': 'none'}),
                html.Img(src=r"assets/négatif/CastleWC_newYork.png",width='50%',id="négatif-newYork", style= {'display': 'none'}),
                html.Img(src=r"assets/négatif/CastleWC_santaFe.png",width='50%',id="négatif-santaFe", style= {'display': 'none'}),
                html.Img(src=r"assets/négatif/CastleWC_sequoiaLodge.png",width='50%',id="négatif-sequoiLodge", style= {'display': 'none'})
             ], id="hotel-negatif", style= {'display': 'none'})
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
    
    
@app.callback([Output('titre-2019', 'style'),
               Output('titre-2020', 'style'),
               Output('titre-2021', 'style'),
               Output('titre-2022', 'style'),
               Output('titre-2023', 'style')
               ],
               [Input('liste_choix_date_titre', 'value')])

def DateChangeTitre(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]
    
@app.callback([Output('positif-2019', 'style'),
               Output('positif-2020', 'style'),
               Output('positif-2021', 'style'),
               Output('positif-2022', 'style'),
               Output('positif-2023', 'style')
               ],
               [Input('liste_choix_date_positif', 'value')])

def DateChangePositif(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]

@app.callback([Output('négatif-2019', 'style'),
               Output('négatif-2020', 'style'),
               Output('négatif-2021', 'style'),
               Output('négatif-2022', 'style'),
               Output('négatif-2023', 'style')
               ],
               [Input('liste_choix_date_negatif', 'value')])

def DateChangeNégatif(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]


@app.callback([Output('titre-cheyenne', 'style'),
               Output('titre-davyCrockettRanch', 'style'),
               Output('titre-newportBay', 'style'),
               Output('titre-newYork', 'style'),
               Output('titre-santaFe', 'style'),
               Output('titre-sequoiLodge', 'style')
               ],
               [Input('liste_choix_hotel_titre', 'value')])

def HotelChangeTitre(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "6":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]

@app.callback([Output('positif-cheyenne', 'style'),
               Output('positif-davyCrockettRanch', 'style'),
               Output('positif-newportBay', 'style'),
               Output('positif-newYork', 'style'),
               Output('positif-santaFe', 'style'),
               Output('positif-sequoiLodge', 'style')
               ],
               [Input('liste_choix_hotel_positif', 'value')])

def HotelChangePositif(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "6":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]

@app.callback([Output('négatif-cheyenne', 'style'),
               Output('négatif-davyCrockettRanch', 'style'),
               Output('négatif-newportBay', 'style'),
               Output('négatif-newYork', 'style'),
               Output('négatif-santaFe', 'style'),
               Output('négatif-sequoiLodge', 'style')
               ],
               [Input('liste_choix_hotel_negatif', 'value')])

def HotelChangeNegatif(value):
    if value == "1":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "2":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "3":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "4":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'},
                {'display': 'none'}]
    if value == "5":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "6":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]


















    
@app.callback( [Output('hotel-titre', 'style'),
                Output('hotel-positif', 'style'),
                Output('hotel-negatif', 'style')
                ],
                [Input('liste_choix_corpus_hotel', 'value')])
def HotelChangeCorpus(value):
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

@app.callback( [Output('pays-titre', 'style'),
                Output('pays-positif', 'style'),
                Output('pays-negatif', 'style')
                ],
                [Input('liste_choix_corpus_pays', 'value')])
def PaysChangeCorpus(value):
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

@app.callback( [Output('titre-Allemagne', 'style'),
                Output('titre-Belgique', 'style'),
                Output('titre-Espagne', 'style'),
                Output('titre-France', 'style'),
                Output('titre-Italie', 'style'),
                Output('titre-Pays-Bas', 'style'),
                Output('titre-Royaume-Uni', 'style'),
                Output('titre-Suisse', 'style')
                ],
                [Input('liste_choix_pays_titre', 'value')])
def PaysChangeTitre(value):
    if value == "1":
        return [{'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "2":
        return [{'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "3":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "4":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "5":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "6":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "7":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'}]
    
    if value == "8":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'}]

@app.callback( [Output('positif-Allemagne', 'style'),
                Output('positif-Belgique', 'style'),
                Output('positif-Espagne', 'style'),
                Output('positif-France', 'style'),
                Output('positif-Italie', 'style'),
                Output('positif-Pays-Bas', 'style'),
                Output('positif-Royaume-Uni', 'style'),
                Output('positif-Suisse', 'style')
                ],
                [Input('liste_choix_pays_positif', 'value')])
def PaysChangePositif(value):
    if value == "1":
        return [{'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "2":
        return [{'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "3":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "4":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "5":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "6":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "7":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'}]
    
    if value == "8":
        return [{'display': 'none'},
                 {'display': 'none'},
                {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'}]

@app.callback( [Output('négatif-Allemagne', 'style'),
                Output('négatif-Belgique', 'style'),
                Output('négatif-Espagne', 'style'),
                Output('négatif-France', 'style'),
                Output('négatif-Italie', 'style'),
                Output('négatif-Pays-Bas', 'style'),
                Output('négatif-Royaume-Uni', 'style'),
                Output('négatif-Suisse', 'style')
                ],
              [Input('liste_choix_pays_negatif', 'value')])
def PaysChangeNegatif(value):
    if value == "1":
        return [{'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "2":
        return [{'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
     
    if value == "3":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "4":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "5":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "6":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'},
                 {'display': 'none'}]
    
    if value == "7":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'block'},
                 {'display': 'none'}]
    
    if value == "8":
        return [{'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
                 {'display': 'none'},
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

@app.callback([Output("no-output", "style")],
              [Input('Actu', 'n_clicks')])
def Actualisation(n_clicks):
    if n_clicks is not None: 
        global disney
        preparation(disney)
    return [{"display":"none"}]

#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
