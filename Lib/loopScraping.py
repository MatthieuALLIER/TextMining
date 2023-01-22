# -*- coding: utf-8 -*-
"""
Boucle des urls
"""
from selenium import webdriver
from Lib import scrapping
import pandas as pd

def loopScraping(df):
    
    disney = pd.DataFrame(columns=["Prenom", "Note", "Pays", "Titre", "Positif",
                               "Négatif", "Date séjour", "Date commentaire", "hotel"])
    
    urls = ["https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews",
            "https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews",
            "https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews",
            "https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews",
            "https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews",
            "https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews"
            ]
    DFnames = ["newYork", "newportBay", "sequoiaLodge", "cheyenne", "santaFe", "davyCrockettRanch"]
    
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    for num in range(len(urls)):
        url = urls[num]
        nameDF = DFnames[num]
        DF = scrapping.Scrapping(driver, url, df)
        DF["hotel"] = nameDF
        disney = disney.append(DF)        
        disney = pd.merge(disney, df, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    return disney