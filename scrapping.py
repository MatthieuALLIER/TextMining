# -*- coding: utf-8 -*-
"""
Fichier scraping Booking Disneyland
"""
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def Scrapping(driver, url):
    userNames = []
    notes = []
    country = []
    titles = []
    posComs = []
    posNeg = []
    travelDate = []
    comDate = []  
    
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
                
            userNames.append(name)
            notes.append(note)
            country.append(pays)
            titles.append(titre)
            posComs.append(compos)
            posNeg.append(comneg)
            travelDate.append(date_sejour)
            comDate.append(date_commentaire)
            
        time.sleep(1)
        try:
            driver.find_element(By.CLASS_NAME,  "pagenext").click()
        except:
            return {"userNames":userNames, 
                    "notes":notes,
                    "country":country,
                    "titles":titles,
                    "posComs":posComs,
                    "posNeg":posNeg,
                    "travelDate":travelDate,
                    "comDate":comDate}
        
        
