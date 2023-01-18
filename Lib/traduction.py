# -*- coding: utf-8 -*-
"""
Traduction
"""
from deep_translator import GoogleTranslator
from langdetect import detect

def tradList(texts):
    translator = GoogleTranslator(source='auto', target='fr')
    n = len(texts)
    for i in range(n):
        print(i)
        if isinstance(texts[i], str):
            try:
                if detect(texts[i]) != "fr":
                    texts.loc[i] = translator.translate(texts[i])
            except:
                texts[i] = None                
    return texts
