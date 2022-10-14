"""
Created by: DSA LinGene - Eugene
Email: dsa.lingene@outlook.com
"""

import mysql.connector
import pandas as pd
from time import time
import config as cfg
import helper as helper

# Dump PKL
# 1. Database/au_towns.pkl
# 2. Database/META_DATA_INDEX.pkl

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 01 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Dumping to au_towns.pkl from database")

t_start = time()

# Get Header
cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'],
                              host=cfg.mysql['host'], database='new_db')
cursor = cnx.cursor()
cursor.execute("SHOW columns FROM new_db.au_towns")
town_header = cursor.fetchall()

# Get Rows
cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'],
                              host=cfg.mysql['host'], database='new_db')

cursor = cnx.cursor()
cursor.execute("SELECT * FROM new_db.au_towns")
town_result = cursor.fetchall()

# Into DataFrame
town_header = [h[0] for h in town_header]
town_result_data = [{h: r for h, r in zip(town_header, row)} for row in town_result]

au_towns = pd.DataFrame.from_dict(town_result_data)

au_towns.to_pickle('Database/au_towns.pkl')

del au_towns

print('au_towns:', (time() - t_start) / 60, 'min')

print("Dumping to META_DATA_INDEX.pkl from database")

t_start = time()

# Get Header
cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'],
                              host=cfg.mysql['host'], database='new_db')
cursor = cnx.cursor()
cursor.execute("SHOW columns FROM new_db.META_DATA_INDEX_copy")
MDI_header = cursor.fetchall()
cnx.close()

# Get Rows
cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'],
                              host=cfg.mysql['host'], database='new_db')
cursor = cnx.cursor()
cursor.execute("SELECT * FROM new_db.META_DATA_INDEX_copy")
MDI_result = cursor.fetchall()
cnx.close()

# Into DataFrame
MDI_header = [h[0] for h in MDI_header]
MDI_result_data = [{h: r for h, r in zip(MDI_header, row)} for row in MDI_result]

META_DATA_INDEX = pd.DataFrame.from_dict(MDI_result_data)
del MDI_result

META_DATA_INDEX.to_pickle('Database/META_DATA_INDEX.pkl')
del META_DATA_INDEX

print('META_DATA_INDEX:', (time() - t_start) / 60, 'min')

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 01 ------------------------------")
print("-----------------------------------------------------------------------------")
