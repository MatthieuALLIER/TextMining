# -*- coding: utf-8 -*-
"""
Boucle des urls
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

urls = ["https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews",
        "https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews",
        "https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews",
        "https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews",
        "https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews",
        "https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews"]
DFnames = ["newYork", "newportBay", "sequoiaLodge", "cheyenne", "santaFe", "davyCrockettRanch"]

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
for num in range(len(urls)):
    url = urls[num]
    nameDF = DFnames[num]
    exec(open('GIT/scrapping.py').read())
    exec(open('GIT/traitement.py').read())