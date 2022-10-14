"""
Created by: DSA LinGene - Eugene
Email: dsa.lingene@outlook.com
"""
import math
import pickle
# import numpy as np
# from gensim import corpora
# from gensim.models import TfidfModel
# from gensim.models import KeyedVectors
import helper as helper

# Dump PKL
# 1. Database/processed/towns.pkl
# 2. Keywords/business_keywords.pkl
# 3. Keywords/premium_keywords.pkl
# 4. Keywords/organic_keywords/{1, 2, ..., 15}.pkl
# 5. Keywords/org_key_vec.pkl
# 6. Database/processed/biz_coors/{1, 2, ..., 15}.pkl
# 7. Database/processed/suburb_coors.pkl

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 02 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading town data from au_towns")
au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))

# Felix: Never used Database/processed/towns.pkl
# towns = au_towns['name'].tolist()
# towns = {t: i for i, t in enumerate(set(towns))}
# pickle.dump(towns, open('Database/processed/towns.pkl', 'wb'))

print("Loading data from META_DATA_INDEX")

# META_DATA_INDEX = pickle.load(open('Database/META_DATA_INDEX.pkl', 'rb'))

with open('Database/META_DATA_INDEX.pkl', 'rb') as f:
    META_DATA_INDEX = pickle.load(f)

# def fn(x):
#     return [w for w in x if w is not None and len(w) > 2]
# ------------------------------------ Keywords/business_keywords.pkl ----------------------------------------------
print("Dumping for business_keywords")
# B_TOWN = {}
# # TOWN_B = {}
# for mid, town_id in zip(META_DATA_INDEX.id, META_DATA_INDEX.town_id):
#     if town_id > 0:
#         B_TOWN[mid] = town_id
#
#         # if town_id in TOWN_B:
#         #     TOWN_B[town_id].append(mid)
#         # else:
#         #     TOWN_B[town_id] = [mid]
#
META_DATA_INDEX['coordinates'] = META_DATA_INDEX.coordinates.apply(lambda x: helper.point_to_tuple(x))

# {1: ['Danoz Direct Alexandria', (-33.8979427, 151.1951919), 114.0]}
B_Business = {}
for mid, name, b, coordinates, town_id, town_name in zip(META_DATA_INDEX.id, META_DATA_INDEX.business_name,
                                                         META_DATA_INDEX.B, META_DATA_INDEX.coordinates,
                                                         META_DATA_INDEX.town_id, META_DATA_INDEX.TOWN_NAME):
    # print(mid)
    # print(name)
    # print(b)
    # print(coordinates)
    # print(town_id)
    if b is not None and len(b) > 2:
        if town_id > 0:
            tid = town_id
        else:
            tid = None
        B_Business[mid] = [name, coordinates, tid, town_name]
        # print(B_Business)

# META_DATA_INDEX_B = META_DATA_INDEX['B'].apply(lambda x: [w for w in x if w is not None and len(w) > 2])
# business_keywords = {idx: words for idx, words in zip(META_DATA_INDEX.id, META_DATA_INDEX_B)}

pickle.dump(B_Business, open('Keywords/business_keywords.pkl', 'wb'))
del B_Business

# ------------------------------------ Keywords/premium_keywords.pkl ----------------------------------------------
print("Dumping for premium_keywords")
META_DATA_INDEX['PREMIUM'] = 0
META_DATA_INDEX.loc[(~META_DATA_INDEX.S2.isnull()) | (~META_DATA_INDEX.T3.isnull()), 'PREMIUM'] = 1

try:
    for col in ['B', 'S1', 'S2', 'T1', 'T2', 'T3']:
        if col not in ['S1', 'S2']:
            META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list(x, col))
        elif col == 'S2':
            META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list_S2(x, col))
        else:
            META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list_S(x, col))
except Exception as e:
    print(e)

premium_keywords = {idx: {'S2': s2, 'T3': t3}
                    for idx, s2, t3 in zip(META_DATA_INDEX.id, META_DATA_INDEX.S2, META_DATA_INDEX.T3)}

pickle.dump(premium_keywords, open('Keywords/premium_keywords.pkl', 'wb'))
del premium_keywords

# ------------------------------------ Keywords/organic_keywords/{}.pkl ----------------------------------------------
print("Dumping for organic_keywords")

resultBT123 = META_DATA_INDEX.B + META_DATA_INDEX.T1 + META_DATA_INDEX.T2 + META_DATA_INDEX.T3
organic_keywords = {idx: words if len(words) != 0 else [None] for idx, words in zip(META_DATA_INDEX.id, resultBT123)}
del resultBT123
organic_keywords = {k: [vi for vi in v if vi is not None] for k, v in organic_keywords.items()}

# print('organic_keywords Length : ' + str(len(organic_keywords)))

bt = 0
for item in helper.chunks(organic_keywords, 100000):
    bt += 1
    pickle.dump(item, open('Keywords/organic_keywords/{}.pkl'.format(bt), 'wb'))

# ------------------------ Keywords/org_key_vec.pkl ------------------------------
# Felix: Never used Keywords/org_key_vec.pkl

# print("Dumping for org_key_vec")
#
# w2v = KeyedVectors.load_word2vec_format('Text Embedding/GloVe/W2V.50d.txt')
#
# documents = list(organic_keywords.values())
#
# mydict = corpora.Dictionary([doc for doc in documents])
# corpus = [mydict.doc2bow(doc) for doc in documents]
# tfidf = TfidfModel(corpus, smartirs='ntc')
#
# mydict.save('Keywords/mydict')
# tfidf.save('Keywords/tfidf')
#
# org_key_tfidf = {}
#
# for k, v in organic_keywords.items():
#     corp = mydict.doc2bow(v)
#     org_key_tfidf[k] = {mydict[k]: v for k, v in tfidf[corp]}

# org_key_vec = {}
#
# for k, v in organic_keywords.items():
#     corp = mydict.doc2bow(v)
#     vec = [w2v[mydict[k].lower()] * v for k, v in tfidf[corp] if mydict[k].lower() in w2v]
#
#     if len(vec) != 0:
#         vec = np.sum(vec, axis=0)
#         vec = vec / np.linalg.norm(vec)
#         org_key_vec[k] = vec
#     else:
#         org_key_vec[k] = []
#
# pickle.dump(org_key_vec, open('Keywords/org_key_vec.pkl', 'wb'))

del organic_keywords
# del org_key_vec

# ------------------------- Database/processed/biz_coors/{}.pkl ------------------------------------
# Felix: Never used Database/processed/biz_coors/{}.pkl

# print("""
# # Obtain Business Coordinates
# """)
#
# META_DATA_INDEX['coordinates'] = META_DATA_INDEX.coordinates.apply(lambda x: helper.point_to_tuple(x))
#
# biz_coors = {}
# for r in META_DATA_INDEX.iterrows():
#     try:
#         row = r[1]
#         biz_id = row['id']
#         biz_coors[biz_id] = row['coordinates']
#
#     except Exception as e:
#         print(e)
#
# bt = 0
# for item in helper.chunks(biz_coors, 100000):
#     bt += 1
#     pickle.dump(item, open('Database/processed/biz_coors/{}.pkl'.format(bt), 'wb'))

# ------------------------- Database/processed/suburb_coors.pkl ------------------------------------

# Felix: Never used Database/processed/biz_coors/{}.pkl

# print("""
# # Suburb Coordinates
# """)
#
# au_towns = au_towns[(~au_towns.area_sq_km.isnull()) & (~au_towns.name.isnull())
#                     & (~au_towns.latitude.isnull()) & (~au_towns.longitude.isnull())]
# suburb_coors = {row[1]['id']: {'radius': np.math.sqrt(row[1]['area_sq_km']) / np.math.pi,
#                                'suburb': row[1]['name'],
#                                'lat_long': (float(row[1]['latitude']), float(row[1]['longitude']))}
#                 for row in au_towns.iterrows()}
#
# pickle.dump(suburb_coors, open('Database/processed/suburb_coors.pkl', 'wb'))

del META_DATA_INDEX
del au_towns

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 02 ------------------------------")
print("-----------------------------------------------------------------------------")
