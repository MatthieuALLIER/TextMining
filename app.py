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
        
    ], id="index-tab", style= {'display': 'block'}),
    html.Div([
        dbc.Tabs([
                    dbc.Tab(label="KPIs", tab_id="kpi"),
                    dbc.Tab(label="Acquisition", tab_id="getData")     
                ],
                id="tabPanelData",
                active_tab="kpi",)
    ], id="data-tab", style= {'display': 'none'}),
    html.Div([
        dbc.Tabs([
                    dbc.Tab(label="Date", tab_id="date"),
                    dbc.Tab(label="Pays", tab_id="pays"),
                    dbc.Tab(label="Hôtel", tab_id="hotel"),
                    dbc.Tab(label="Mots liés", tab_id="lies")    
                ],
                id="tabPanelAnalyse",
                active_tab="date")
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
        return [{'display': 'block'},{'display': 'none'},{'display': 'none'}]
    if value == "data":
        return [{'display': 'none'},{'display': 'block'},{'display': 'none'}]
    if value == "analyse":
        return [{'display': 'none'},{'display': 'none'},{'display': 'block'}]

#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
