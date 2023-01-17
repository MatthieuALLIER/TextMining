# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

import pandas as pd

from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

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
            dbc.Tab(label="Accueil", tab_id="index", value='tabAccueil'),
            dbc.Tab(label="Données", tab_id="data", value='tabDonnees'),
            dbc.Tab(label="Analyse", tab_id="analyse", value='tabAnalyse')           
        ],
        id="tabPanel",
        active_tab="index",
    )
])

#Content
PageContent = dbc.Container([
    html.Div([
        
    ], id="index-tab"),
    html.Div([
    ], id="data-tab"),
    html.Div([
    ], id="analyse-tab")
])

#Apparence
app.layout = html.Div([TABPANEL, PageContent])

#Callback
@app.callback(Output('tab1', 'children'),
              [Input('tabs', 'value')])
def update_tabs(value):
    if value == 'tabDonnees':
        return dbc.Tabs([
                    dbc.Tab(label="KPIs", tab_id="kpi"),
                    dbc.Tab(label="Acquisition", tab_id="getData")       
                ],
                id="tabPanelData",
                active_tab="kpi")
    if value == 'tabAnalyse':
        return dbc.Tabs([
                    dbc.Tab(label="Date", tab_id="date"),
                    dbc.Tab(label="Pays", tab_id="pays"),
                    dbc.Tab(label="Hôtel", tab_id="hotel"),
                    dbc.Tab(label="Mots liés", tab_id="lies")    
                ],
                id="tabPanelAnalyse",
                active_tab="date")
    
    
#Lauch
if __name__ == '__main__':
    app.run_server()
