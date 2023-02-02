#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#disney = df de base

###########---------------------  DF pour le sunburst   ------------------####################

class Fig :

    def __init__(self, df,df_sunb, df_pays_nb, agg_df):
        self.__df = df
        self.__df_sunb = df_sunb
        self.__df_pays_nb = df_pays_nb
        self.__agg_df = agg_df
        
#Sunburst Hotel > Pays > Note
    def get_fig_sunburst(self):
        return px.sunburst(self.__df_sunb, title="Sunburst nombre de commentaires par hotel, pays et par note", path=['hotel', 'Pays', 'Note'],values='nbc', color='Note', hover_data=['nbc'], color_discrete_sequence=px.colors.sequential.Plasma).update_layout({'plot_bgcolor':'rgb(39, 43, 48)', 'paper_bgcolor':'rgb(39, 43, 48)', 'font_color':'white'})

#Un graphique à courbes pour montrer l'évolution des notes au fil des mois.
    
    def get_fig_plot_comm(self):
       data = [go.Scatter(x=self.__agg_df.index, y=self.__agg_df['Note'])]
       layout = go.Layout(title='Evolution des notes au fil des mois', xaxis=dict(title='Month'), yaxis=dict(title='Note'))
       return go.Figure(data=data, layout=layout)
 

#Carte du monde avec nb de commentaire par pays

    def get_fig_map(self):
        return px.choropleth(data_frame=self.__df_pays_nb,
                    locations='Pays',  # colonne contenant les noms des pays
                    locationmode='country names',
                    color='occ',  # colonne contenant le nombre d'occurrences
                    hover_name='Pays',
                    title='Nombre d\'occurrences par pays')

