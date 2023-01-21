# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

import pandas as pd

import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import mysql.connector
from mysql.connector import Error

from Lib import rawToBDD, nettoyage, scrapping, traitement, traduction

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
pays = pd.DataFrame(disney, columns=['pays', 'id_pays'])

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
            html.P("Date")
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

#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
