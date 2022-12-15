# -*- coding: utf-8 -*-
"""

"""
import os, pandas as pd
DFnames = ["cheyenne", "newYork", "newportBay", "sequoiaLodge", "santaFe", "davyCrockettRanch"]

for i in range(len(os.listdir("./data/"))): 
    file = os.listdir("./data/")[i]
    DF = pd.read_csv("./data/"+file, index_col=0)
    nameDF = DFnames[i]
    globals()[nameDF] = DF
    