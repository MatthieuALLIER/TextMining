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



class Fig :

    def __init__(self, df,df_sunb, df_pays_nb):
        self.__df = df
        self.__df_sunb = df_sunb
        self.__df_pays_nb = df_pays_nb
        
#Sunburst Hotel > Pays > Note
    def get_fig_sunburst(self):
        return px.sunburst(self.__df_sunb, title="Sunburst nombre de commentaires par hotel, pays et par note", path=['hotel', 'Pays', 'Note'],values='nbc', color='Note', hover_data=['nbc'], color_discrete_sequence=px.colors.sequential.Plasma).update_layout({'plot_bgcolor':'rgb(39, 43, 48)', 'paper_bgcolor':'rgb(39, 43, 48)', 'font_color':'white'})

#Un graphique à courbes pour montrer l'évolution des notes au fil des mois.
    
#en cours    

#Carte du monde avec nb de commentaire par pays

    def get_fig_map(self)
        return fig = px.choropleth(data_frame=sel.__df_pays_nb,
                    locations='Pays',  # colonne contenant les noms des pays
                    locationmode='country names',
                    color='occ',  # colonne contenant le nombre d'occurrences
                    hover_name='Pays',
                    title='Nombre d\'occurrences par pays')

