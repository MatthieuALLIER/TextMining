# -*- coding: utf-8 -*-
"""
Fichier scraping Booking Disneyland
"""
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import emoji
import pandas as pd
from deep_translator import GoogleTranslator
from langdetect import detect

def nettoyageRow(name, note, pays, titre, compos, comneg, date_sejour, date_commentaire):
    
    translator = GoogleTranslator(source='auto', target='fr')
    
    if type(note) == str:
        note = float(note.replace(" ", "").replace(",", "."))
    else:
        note = "Inconnu"

    if type(pays) == str:
        pays = pays[2:]
    else:
        pays = "Inconnu"

    if type(titre) == str:
        titre = titre.split("\n")[1].split("\xa0")[0]
        titre = emoji.replace_emoji(titre, replace="")
        try:
            if detect(titre) != "fr":
                titre = translator.translate(titre)
        except:
            titre = "Inconnu"
        titre = titre.replace("'", "")
    else:
        titre = "Inconnu"

    if type(compos) == str:
        compos = compos.replace("\n", " ")
        compos = emoji.replace_emoji(compos, replace="")
        try:
            if detect(compos) != "fr":
                compos = translator.translate(compos)
        except:
            compos = "Inconnu"
        compos = compos.replace("'", "")
    else:
        compos = "Inconnu"


    if type(comneg) == str:
        comneg = comneg.replace("\n", " ")
        comneg = emoji.replace_emoji(comneg, replace="")        
        try:
            if detect(comneg) != "fr":
                comneg = translator.translate(comneg)
        except:
            comneg = "Inconnu"
        comneg = comneg.replace("'", "")
    else:
        comneg = "Inconnu"

    if type(date_sejour) == str:
        date_sejour = " ".join(date_sejour.split("\n")[1].split("\xa0"))
    else:
        date_sejour = "Inconnu"

    if type(date_commentaire) == str:
        date_commentaire = " ".join(date_commentaire.split("\n")[1].split("\xa0"))
    else:
        date_commentaire = "Inconnu"
    
    return [name, note, pays, titre, compos, comneg, date_sejour, date_commentaire]
        
def Scrapping(driver, url, df):
    DF = pd.DataFrame(columns=["Prenom", "Note", "Pays", "Titre", "Positif",
                               "Négatif", "Date séjour", "Date commentaire"])
    doublon = 0
    
    driver.get(url)
    try:
        driver.find_element(By.ID, "onetrust-reject-all-handler").click()
    except:
        pass
    
    while(True):    
        content = driver.page_source
        soup = BeautifulSoup(content)
        for a in soup.findAll(attrs={"class":"review_list_new_item_block"}):
            try:
                name = a.find("span", attrs={"class":"bui-avatar-block__title"}).text
            except:
                name = None
            try:
                note = a.find("div", attrs={"class":"bui-review-score__badge"}).text
            except:
                note = None
            try:
                pays = a.find("span", attrs={"class":"bui-avatar-block__subtitle"}).text
            except:
                pays = None
            try:
                titre = a.find("h3", attrs={"class":"c-review-block__title c-review__title--ltr"}).text
            except:
                titre = None
            
            #Commentaires
            try:
                compos = None
                comneg = None
                for com in a.findAll("div", attrs={"class":"c-review__row"}):
                    if com.find("span", attrs={"class":"bui-u-sr-only"}).text == "A aimé":
                        compos = com.find("span", attrs={"class":"c-review__body"}).text
                    elif com.find("span", attrs={"class":"bui-u-sr-only"}).text == "N'a pas aimé":
                        comneg = com.find("span", attrs={"class":"c-review__body"}).text
            except:
                pass
            
            #Dates
            try:
                leftBloc = a.find("div", attrs={"class":"bui-grid__column-3 c-review-block__left"})
                try:
                    date_sejour = leftBloc.find("span", attrs={"class":"c-review-block__date"}).text
                except:
                    date_sejour = None
            except:
                date_sejour = None
            
            try:
                rightBloc = a.find("div", attrs={"class":"bui-grid__column-9 c-review-block__right"})
                try:
                    date_commentaire = rightBloc.find("span", attrs={"class":"c-review-block__date"}).text
                except:
                    date_commentaire = None
            except:
                date_commentaire = None
            
            row = nettoyageRow(name, note, pays, titre, compos, comneg, date_sejour, date_commentaire)
            if any([row == i[:-1] for i in df.values.tolist()]):
                doublon += 1
                
            if doublon == 2:
                break
            else:
                DF.loc[len(DF)] = row
        if doublon < 2:
            time.sleep(1)
            try:
                driver.find_element(By.CLASS_NAME,  "pagenext").click()
            except:                
                DF = DF.drop_duplicates()
                return DF
        else:
            DF = DF.drop_duplicates()
            return DF
        
        
