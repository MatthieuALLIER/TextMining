# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:12:04 2023

@author: mallier
"""

#Utils
import pandas as pd
import json

#Dash
import dash
from dash import Dash, html, dcc, Input, Output, ctx, dash_table
import dash_bootstrap_components as dbc

#MySQL
import mysql.connector
from mysql.connector import Error

#Lib interne
from Lib import loopScraping, rawToBDD
from fonctions_analyse import preparation

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

f = open('data/datas.json')
datas = json.load(f)
  
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
    dcc.Store("datas"),
    html.Div([], id="no-output", style= {'display': 'none'}),
    html.Div([
        #Accueil
        html.H2("Ce projet avait pour objectif de récupérer les données concernant les commentaires de 6 hôtels apparteant à Disney."),
        html.H2("Notre groupe s'est concentré sur Booking.com"),
        html.Img(src=r"assets/Chateau_disney.jpg", width="100%"),
        html.H2("Cette application contient 3 onglets : un premier pour actualiser le scrapping, un autre pour voir les analyses. "),
        
        
    ], id="index-tab", style= {'display': 'block'}),
    html.Div([
        dbc.Tabs([
                    dbc.Tab(label="KPIs", tab_id="kpi"),
                    dbc.Tab(label="Acquisition", tab_id="getData")     
                ], id="tabPanelData", active_tab="kpi"),
        html.Div([
            #Construction auto
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

@app.callback([Output("kpi-tab", "children")],
              [Input("datas", "data")])

def constructionDataeTab(data):
    global disney
    nbAvis = data["nbAvis"]
    nbGood = data["nbGood"]
    nbBad = data["nbBad"]
    dateMin = data["dateMin"]
    dateMax = data["dateMax"]
    nbPays = data["nbPays"]
    nbPays200 = data["nbPays200"]
    noteMin = data["noteMin"]
    noteAvg = data["noteAvg"]
    noteMax = data["noteMax"]
    
    children = html.Div([], style = {"display":"flex"})
    children.children.append(
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
        ], style = {"width":"25%"})
    )
    children.children.append(
        html.Div([
            dash_table.DataTable(
                data=disney.to_dict('records'),
                columns=[{"name": i, "id": i} for i in disney.columns],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_table={
                    'height': 500,
                    'overflowY': 'scroll',
                    'width': "100%"
                },
                sort_action="native"
            )            
        ], style = {"width":"75%"})
    )
    return [children]

@app.callback([Output("analyse-tab", "children")],
              [Input("datas", "data")])
def constructionAnalyseTab(data):
    
    annee = data["annee"]
    liste_pays = data["liste_pays"]    
    liste_sim = ['séjour','personnel','prix','bien','super','cher']
    
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
            
            mesureDiv = html.Div([], id=dimension+"-"+mesure, style = {"display":"none"})
            
            if dimension == "date":
                options = optionsDate
            elif dimension == "pays":
                options = optionsPays
            elif dimension == "hotel":
                options = optionsHotel
               
            dimDatas = dimension[0].upper() +dimension[1:]
            mesDatas = mesure.replace("é","e")
            DfDimension = pd.DataFrame(data[mesDatas+dimDatas][0]).reset_index()
            SimilariteMot = pd.DataFrame(data[mesDatas+dimDatas][1], columns = ["Similaire","Taux"])
            
            imgDiv = html.Div([], style={"display":"flex"})
            i = 1
            for modalite in options.values():
                if i%5 == 0:
                    mesureDiv.children.append(imgDiv)
                    imgDiv = html.Div([], style={"display":"flex"})
                img = html.Div([
                    html.H4(modalite, style={"text-align":"center"}),
                    html.Img(src=r"assets/"+mesure+"/CastleWC_"+modalite+".png", width="100%")
                ], style={"width":"25%"})
                imgDiv.children.append(img)
                i += 1
                
            mesureDiv.children.append(imgDiv)
            
            dt = dash_table.DataTable(
                data=DfDimension.to_dict('records'),
                columns=[{"name": i, "id": i} for i in DfDimension.columns],
                style_table={
                    'height': 400,
                    'overflowY': 'scroll',
                    'width': "100%"
                },
                sort_action="native"
            )            
            mesureDiv.children.append(dt)
            
            similiteDiv = html.Div([
                html.P("Mots liés avec : ("+", ".join(liste_sim)+")"),
                dash_table.DataTable(
                    data=SimilariteMot.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in SimilariteMot.columns],
                    style_table={
                        'height': 400,
                        'width': "30%"
                    },
                    sort_action="native"
                )
            ])            
            mesureDiv.children.append(similiteDiv)                
            
            dimensionTab.children.append(mesureDiv)
            
        children.append(dimensionTab)

    return [children]

#Preparation callback
optionsDate = {k: k for k in list(map(str, list(set(datas["annee"]))))}
optionsPays = {k: k for k in datas["liste_pays"]}
optionsHotel = {k: k for k in list(set(disney.hotel))}

outputs = []
inputs = []
for dimension in ["date","pays","hotel"]:
    
    inputs.append(Input("dd_"+dimension+"_mesure", "value"))
    
    for mesure in ["titre","positif","négatif"]:
        
        outputs.append(Output(dimension+"-"+mesure, "style"))
            
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
def showMask(value1,value2,value3):
    
    trigger = ctx.triggered_id
    
    if trigger == None:
        return dash.no_update
    
    res = [{'display': 'none'} for i in range(len(outIds))]
    
    values = [value1,value2,value3]
    value = values[inpIds.index(trigger)]
    
    for dimension in ["date","pays","hotel"]:
        
        if trigger == "dd_"+dimension+"_mesure":
            outIndex = outIds.index(dimension+"-"+value)
            res[outIndex] = {'display': 'block'}
            return res
    
@app.callback([Output("datas", "data")],
              [Input('MAJ', 'n_clicks'),
               Input('Actu', 'n_clicks')])

def MiseAJour_Actualisation(maj, actu):
    global datas
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
        return [datas]
    if actu is not None:
        datas = preparation(disney)
        for obj in ["titreDate","titreHotel","titrePays",
                "positifDate","positifHotel","positifPays",
                "negatifDate","negatifHotel","negatifPays"]:
            datas[obj] = list(datas[obj])
            datas[obj][0] = datas[obj][0].to_dict()
        
        with open('data/datas.json', 'w') as f:
            json.dump(datas, f)
            
        print("préparation terminée")
        return [datas]
    else:
        return [datas]

#Lauch
if __name__ == '__main__':
    app.run_server()
