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

#ajoute une colonne nbc avec des 1 et supprime 8 lignes sans le pays
df_sunb = disney.drop(disney.index[disney.iloc[:,2].isnull()],0).assign(nbc = 1)

###########--------------------- DF pour plot comm/mois  ------------------####################

df_commdate = disney

#Séparation mois/annee
df_commdate["Date séjour"] = df_commdate["Date séjour"].apply(lambda x: x.split(" "))
df_commdate["mois"] = [i[0] for i in df_commdate["Date séjour"]]
df_commdate["annee"] = [i[1] for i in df_commdate["Date séjour"]]

# Changement mois en numérique pour traquer l'ordre
old = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre','Décembre']
new = ['01','02','03','04','05','06','07','08','09','10','11','12']
dictio = dict(zip(old, new))
df_commdate['mois'].replace(dictio, inplace=True)

#Moyenne de note par mois
agg_df = df_commdate.groupby(["annee","mois"])["Note"].mean().to_frame().reset_index()

#Nouveau index date
agg_df['date'] = agg_df['annee'].str.cat(agg_df['mois'], sep=' ')
agg_df = agg_df.set_index('date').drop(columns=["annee", "mois"])



###########--------------------- DF pour la world map  ------------------####################

#Création df avec Pays et nb commentaires par Pays puis traduction en anglais pour faire fonctionner le graph
# Pour le df de la carte du monde, déso j'ai pas trouvé plus court, les packages de traductions fonctionnaient pas très bien 

df_pays_nb = disney['Pays'].value_counts().to_frame().reset_index().rename(columns={'index': 'Pays', 'Pays': 'occ'})
print(df_pays_nb)

old_values = ['Finlande', 'La Réunion', 'France', 'Espagne', 'Belgique',
       'Suisse', 'Maroc', 'Guadeloupe', 'États-Unis', 'Allemagne',
       'Tunisie', 'Japon', 'Polynésie française', 'Nouvelle-Calédonie',
       'Brésil', 'Canada', 'Pays-Bas', 'Royaume-Uni', 'Irlande',
       'Singapour', 'Arabie saoudite', 'Israël', 'Australie', 'Malaisie',
       'Portugal', 'Norvège', 'Bulgarie', 'Thaïlande', 'Grèce',
       'République tchèque', 'Argentine', 'Luxembourg', 'Malte',
       'Mexique', 'Brunei', 'Hongrie', 'Géorgie', 'Émirats arabes unis',
       'Roumanie', 'Estonie', 'Gibraltar', 'Pologne', 'Turquie', 'Égypte',
       'Indonésie', 'Italie', 'Koweït', 'Autriche', 'Chine', 'Colombie',
       'Honduras', 'Costa Rica', 'Ukraine', 'Russie', 'Danemark',
       'Lettonie', 'Panama', 'Pérou', 'Qatar', 'Hong Kong', 'Martinique',
       'Algérie', 'Monaco', "Côte-d'Ivoire", 'Afrique du Sud', 'Chypre',
       'Suède', 'Jersey', 'Nouvelle-Zélande', 'Azerbaïdjan', 'Namibie',
       'Philippines', 'Corée du Sud',
       'Slovaquie', 'Venezuela', 'Guyane française', 'Croatie',
       'Chili', 'Taïwan', 'Bénin', 'Madagascar', 'Albanie', 'Bahreïn',
       'Sri Lanka', 'Liban', 'Oman', 'Mozambique', 'Kazakhstan',
       'Mayotte', 'Nigeria', 'Jordanie', 'Lituanie', 'Serbie', 'Iran',
       'Angola', 'Île Maurice', 'Pakistan', 'Cameroun',
       'Saint-Martin (Antilles françaises)', 'Porto Rico',
       'Bosnie-Herzégovine', 'Kosovo', 'Laos', 'Irak', 'Inde', 'Slovénie',
       'Saint-Barthélemy', 'Djibouti', 'Moldavie', 'Andorre', 'Aruba',
       'Crimée', 'Uruguay', 'Islande']

new_values = ['Finland', 'Reunion', 'France', 'Spain', 'Belgium',
       'Switzerland', 'Morocco', 'Guadeloupe', 'United States', 'Germany',
       'Tunisia', 'Japan', 'French Polynesia', 'New Caledonia',
       'Brazil', 'Canada', 'Netherlands', 'United Kingdom', 'Ireland',
       'Singapore', 'Saudi Arabia', 'Israel', 'Australia', 'Malaysia',
       'Portugal', 'Norway', 'Bulgaria', 'Thailand', 'Greece',
       'Czech Republic', 'Argentina', 'Luxembourg', 'Malta',
       'Mexico', 'Brunei', 'Hungary', 'Georgia', 'United Arab Emirates',
       'Romania', 'Estonia', 'Gibraltar', 'Poland', 'Turkey', 'Egypt',
       'Indonesia', 'Italy', 'Kuwait', 'Austria', 'China', 'Colombia',
       'Honduras', 'Costa Rica', 'Ukraine', 'Russia', 'Denmark',
       'Latvia', 'Panama', 'Peru', 'Qatar', 'Hong Kong', 'Martinique',
       'Algeria', 'Monaco', 'Ivory Coast', 'South Africa', 'Cyprus',
       'Sweden', 'Jersey', 'New Zealand', 'Azerbaijan', 'Namibia',
       'Philippines', 'South Korea',
       'Slovakia', 'Venezuela', 'French Guiana', 'Croatia',
       'Chile', 'Taiwan', 'Benin', 'Madagascar', 'Albania', 'Bahrain',
       'Sri Lanka', 'Lebanon', 'Oman', 'Mozambique', 'Kazakhstan',
       'Mayotte', 'Nigeria', 'Jordan', 'Lithuania', 'Serbia', 'Iran',
       'Angola', 'Mauritius', 'Pakistan', 'Cameroon',
       'Saint-Martin (French West Indies)', 'Puerto Rico',
       'Bosnia and Herzegovina', 'Kosovo', 'Laos', 'Iraq', 'India', 'Slovenia',
       'Saint-Barthélemy', 'Djibouti', 'Moldova', 'Andorra', 'Aruba',
       'Crimea', 'Uruguay', 'Iceland']

translation_dict = dict(zip(old_values, new_values))

df_pays_nb['Pays'].replace(translation_dict, inplace=True)

from fonctions_graphiques import Fig
graphs = Fig(disney,df_sunb,df_pays_nb,agg_df)
sunburst = graphs.get_fig_sunburst()
carte = graphs.get_fig_map()

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
        html.Br(),
        html.H5("Ce projet avait pour objectif de récupérer les données concernant les commentaires de 6 hôtels apparteant à Disney."),
        html.Br(),
        html.H5("Notre groupe s'est concentré sur le site Booking.com."),
        html.Br(),
        html.Div([
            html.Img(src=r"assets/Chateau_disney.jpg", height="100%"),
            html.Img(src=r"assets/Disney_Newport_Bay_Club.jpg", height="100%", style = {"padding-left":"10px"})
        ], style = {"height":"250px"}),
        html.Br(),
        html.Br(),
        html.H5("Nous avons récupéré plusieurs éléments concernant les commentaires :"),
        html.Ul(),
            html.Li("La note attribuée"),
            html.Li("La nationalité du donneur de l'avis"),
            html.Li("Le titre de l'avis"),
            html.Li("Le commentaire positif"),
            html.Li("Le commentaire négatif"),
            html.Li("La date du séjour"),
            html.Li("La date du commentaire"),
        html.Br(),
        html.Br(),
        html.H5("Cette application contient 2 onglets : "),
        html.Ul(),
            html.Li("Un premier pour voir les données et actualiser le scrapping"),
            html.Li("Un second pour accéder aux analyses")
        
        
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
            html.Button('Mettre à jour', id='MAJ', style = {"width":"20%", "height":"50px",
                                                            "background-color":"white",
                                                            "border":"2px solid blue",
                                                            "margin":"10px"}),
            html.Button('Actualiser les analyses', id='Actu', style = {"width":"20%", "height":"50px",
                                                            "background-color":"white",
                                                            "border":"2px solid blue",
                                                            "margin":"10px"})
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

def constructionDataTab(data):
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
    
    children = []
    children.append(
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
        ], style = {"display":"flex"})
    )
    children.append(
        html.Div([
            dcc.Graph(figure = sunburst, style={"width":"80%", "margin":"10%"}),
            dcc.Graph(figure = carte, style={"width":"80%", "margin":"10%"})
        ])    
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
