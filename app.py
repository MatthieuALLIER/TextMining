# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

import pandas as pd

import dash
from dash import Dash, html, dcc, Input, Output, State
from wordcloud import WordCloud
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from Lib import nettoyage
from analyse_date import analyseDate

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Disney textmining')
server = app.server
print("Importation des données")
disney=pd.read_csv("data/disney.csv")

#### Nettoyage
# Titre
print("Nettoyage des titres")
 # On enlève les inconnus dans les avis
titre=nettoyage.nettoyage_corpus(disney.Titre)
titre_join = [" ".join(w)for w in titre]
# On enlève les inconnus dans les avis
#titre_join = [w for w in titre_join if not w == "inconnu"]


# Commentairs positifs
print("Nettoyage des commentaires positifs")
positif=nettoyage.nettoyage_corpus(disney.Positif)
positif_join = [" ".join(w)for w in positif]
# On enlève les inconnus dans les avis
#positif_join = [w for w in positif_join if not w == "inconnu"]


# Commentaires négatifs
print("Nettoyage des commentaires négatifs")
negatif=nettoyage.nettoyage_corpus(disney.Négatif)
negatif_join = [" ".join(w)for w in negatif]
# On enlève les inconnus dans les avis
#negatif_join = [w for w in negatif_join if not w == "inconnu"]


# Passage de la colonne date_sejour en format date
print("Formatage des dates")
import dateparser 
date_sejour = disney["Date séjour"].tolist()
date_sejour=[dateparser.parse(date) for date in date_sejour]
annee=[date.year for date in date_sejour]

# Fonction d'analyse par année
titredate=analyseDate(titre_join,annee,"titre")
posdate=analyseDate(positif_join,annee,"positif")
negdate=analyseDate(negatif_join,annee,"négatif")
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
            #Acquisition
            html.P("Acquisition")
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
                   id="liste_choix_corpus_date"
             ),
            html.Div([
               html.Img(id='image_titre_date_2019'),
               html.Img(id='image_titre_date_2020'),
               html.Img(id='image_titre_date_2021'),
               html.Img(id='image_titre_date_2022'),
               html.Img(id='image_titre_date_2023')
            ], id="date-titre", style= {'display': 'none'}),
            
            html.Div([
               html.Img(id='image_positifs_date_2019'),
               html.Img(id='image_positifs_date_2020'),
               html.Img(id='image_positifs_date_2021'),
               html.Img(id='image_positifs_date_2022'),
               html.Img(id='image_positifs_date_2023')
            ], id="date-positif", style= {'display': 'none'}),
            
            html.Div([
               html.Img(id='image_negatifs_date_2019'),
               html.Img(id='image_negatifs_date_2020'),
               html.Img(id='image_negatifs_date_2021'),
               html.Img(id='image_negatifs_date_2022'),
               html.Img(id='image_negatifs_date_2023')
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
    
@app.callback( [Output('date-titre', 'style'),
               Output('date-positif', 'style'),
               Output('date-negatif', 'style')
               ],
               [Input('liste_choix_corpus_date', 'value')])
def DateChangeCorpus(value):
    print(value)
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
#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
