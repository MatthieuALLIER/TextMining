#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#disney = df de base

#ajoute une colonne nbc avec des 1 et supprime 8 lignes sans le pays
df_sunb = disney.drop(disney.index[disney.iloc[:,2].isnull()],0).assign(nbc = 1)


class Fig :

    def __init__(self, df,df_sunb):
        self.__df = df
        self.__df_sunb = df_sunb 
        
#Sunburst Hotel > Pays > Note
    def get_fig_sunburst(self):
        return px.sunburst(self.__df_sunb, title="Sunburst nombre de commentaires par hotel, pays et par note", path=['hotel', 'Pays', 'Note'],values='nbc', color='Note', hover_data=['nbc'], color_discrete_sequence=px.colors.sequential.Plasma).update_layout({'plot_bgcolor':'rgb(39, 43, 48)', 'paper_bgcolor':'rgb(39, 43, 48)', 'font_color':'white'})

#Un graphique à courbes pour montrer l'évolution des notes au fil des mois.
    
#en cours    
 

