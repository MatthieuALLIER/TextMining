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
from dash import Dash, html, dcc, Input, Output, State, ctx
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
    
preparation(disney)
 
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
            html.Div([
                html.P("Nombre d'avis : "+str(nbAvis)),
                html.P("Nombre d'avis positifs : "+str(nbGood)),
                html.P("Nombre d'avis négatifs : "+str(nbBad)),
                html.P("Date minimum : "+str(dateMin)),
                html.P("Date maximum : "+str(dateMax)),
                html.P("Nombre de pays : "+str(nbPays)),
                html.P("Nombre de pays avec plus de 200 avis : "+str(nbPays200)),
                html.P("Notes : "),
                html.P("Minimum : "+str(noteMin)),
                html.P("Moyenne : "+str(noteAvg)),
                html.P("Maximum : "+str(noteMax)),
            ], style = {"width":"25%"}),
            html.Div([
                
            ], style = {"width":"75%"})
        ], id="kpi-tab", style= {'display': 'none'}),
        html.Div([
            html.Button('Mettre à jour', id='MAJ'),
            html.Button('Actualiser les analyses', id='Actu')
        ], id="getData-tab", style= {'display': 'none'})
        
    ], id="data-tab", style= {'display': 'none'}),
    html.Div([
        #Construction auto
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

@app.callback([Output("analyse-tab", "children")],
              [Input("no-output", "children")])
def constructionAnalyseTab(n_clicks):
    children = []
    optionsDate = {k: k for k in list(map(str, list(set(annee))))}
    optionsPays = {k: k for k in liste_pays}
    optionsHotel = {k: k for k in list(set(disney.hotel))}
    
    TabAnalyse = dbc.Tabs([
        dbc.Tab(label="Date", tab_id="date"),
        dbc.Tab(label="Pays", tab_id="pays"),
        dbc.Tab(label="Hôtel", tab_id="hotel")   
    ], id="tabPanelAnalyse", active_tab="date")
    
    children.append(TabAnalyse)
    
    for dimension in ["date","pays","hotel"]:
        
        dimensionTab = html.Div([], id=dimension+"-tab", style= {'display': 'none'})
        
        ddMesure = dcc.Dropdown(
            options={"titre":'Titre', "positif":'Commentaires positifs', "négatif":'Commentaires négatifs'},
            style={'font-size': 20},
            clearable = False,
            id="dd_"+dimension+"_mesure")
        
        dimensionTab.children.append(ddMesure)
        
        for mesure in ["titre","positif","négatif"]:
            
            mesureDiv = html.Div([], id=dimension+"-"+mesure, style= {'display': 'none'})
            
            if dimension == "date":
                options = optionsDate
            elif dimension == "pays":
                options = optionsPays
            elif dimension == "hotel":
                options = optionsHotel
                
            ddDimension =  dcc.Dropdown(
                options=options,
                style={'font-size': 20},
                clearable = False,
                id="dd_"+dimension+"_"+mesure)
            
            mesureDiv.children.append(ddDimension)
            
            for modalite in options.values():
                img = html.Img(src=r"assets/"+mesure+"/CastleWC_"+modalite+".png", width='50%', id=mesure+"-"+modalite, style= {'display': 'none'})
                mesureDiv.children.append(img)
                
            dimensionTab.children.append(mesureDiv)
            
        children.append(dimensionTab)

    return [children]

#Preparation callback
optionsDate = {k: k for k in list(map(str, list(set(annee))))}
optionsPays = {k: k for k in liste_pays}
optionsHotel = {k: k for k in list(set(disney.hotel))}

outputs = []
inputs = []
for dimension in ["date","pays","hotel"]:
    
    inputs.append(Input("dd_"+dimension+"_mesure", "value"))
    
    for mesure in ["titre","positif","négatif"]:
        
        inputs.append(Input("dd_"+dimension+"_"+mesure, "value"))
        outputs.append(Output(dimension+"-"+mesure, "style"))
        
        if dimension == "date":
            options = optionsDate
        elif dimension == "pays":
            options = optionsPays
        elif dimension == "hotel":
            options = optionsHotel
        
        for modalite in options.values():
            outputs.append(Output(mesure+"-"+modalite, "style"))
            
outIds = [output.component_id for output in outputs]
inpIds = [inp.component_id for inp in inputs]

@app.callback([Output('date-tab', 'style'),
               Output('pays-tab', 'style'), 
               Output('hotel-tab', 'style')],
               [Input('tabPanelAnalyse', 'active_tab')])
def tabChangeAnalyse(value):
    if value == "date":
        return [{'display': 'block'},
                {'display': 'none'},
                {'display': 'none'},
                ]
    if value == "pays":
        return [{'display': 'none'},
                {'display': 'block'},
                {'display': 'none'}]
    if value == "hotel":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'block'}]
    if value == "lies":
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
        
@app.callback(outputs,
              inputs)
def showMask(value1,value2,value3,value4,value5,value6,value7,value8,value9,value10,value11,value12):
    
    trigger = ctx.triggered_id
    if trigger == None:
        return dash.no_update
    res = [{'display': 'none'} for i in range(len(outIds))]
    
    values = [value1,value2,value3,value4,value5,value6,value7,value8,value9,value10,value11,value12]
    value = values[inpIds.index(trigger)]
    
    for dimension in ["date","pays","hotel"]:
        
        if trigger == "dd_"+dimension+"_mesure":
            outIndex = outIds.index(dimension+"-"+value)
            res[outIndex] = {'display': 'block'}
            return res
        
        for mesure in ["titre","positif","négatif"]:
                    
            if trigger == "dd_"+dimension+"_"+mesure:
                outIndex = outIds.index(mesure+"-"+value)
                res[outIndex] = {'display': 'block'}
                outIndex = outIds.index(dimension+"-"+mesure)
                res[outIndex] = {'display': 'block'}
                return res
    
@app.callback([Output("disney", "data")],
              [Input('MAJ', 'n_clicks'),
               Input('Actu', 'n_clicks')])
def MiseAJour_Actualisation(maj, actu):
    global disney
    global date
    global hotel
    global pays
    global connection
    if maj is not None:
        newAvis = loopScraping.loopScraping(disney)
        date, pays = rawToBDD.StarToSQLInsert(newAvis, date, hotel, pays, connection)       
        disney = disney.append(newAvis)
        disney.to_csv("data/disney.csv", index=False)
        return [disney.to_dict("record")]
    if actu is not None:
        preparation(disney)
        print("préparation terminée")
        return [disney.to_dict("record")]
    raise PreventUpdate()

#Lauch
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
