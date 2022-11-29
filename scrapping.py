# -*- coding: utf-8 -*-
"""
Fichier scraping Booking Disneyland
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

url = "https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviewshttps://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews"

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

userNames = []   
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
            name = a.find("span", attrs={"class":"bui-avatar-block__title"})
        except:
            pass
        
            note = a.find("span", attrs={"class":"bui-review-score__badge"})
            pays = a.find("img", attrs={"src":"bui-review-score__badge"})
            titre = a.find("h3", attrs={"h3":"c-review-block__title c-review__title--ltr"})
            compos=a.find("span", attrs={"class":"c-review__body"})
            comneg=a.find("span", attrs={"class":"c-review__body"})
            date_sejour=a.find("span", attrs={"class":"c-review-block__date"})
            date_commentaire=a.find("span", attrs={"class":"c-review-block__date"})
        
        
        userNames.append(name.text)
    time.sleep(1)
    try:
        driver.find_element(By.CLASS_NAME,  "pagenext").click()
    except:
        break
