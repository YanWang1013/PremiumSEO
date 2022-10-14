import json
import logging
import os
import pickle

import mysql.connector
import spacy
import numpy as np
import helper as helper
import const as const
import config as config
from datetime import datetime, timezone
from itertools import combinations
from logging.handlers import RotatingFileHandler
from time import time

from flask import Flask, request, jsonify
from gensim.models import KeyedVectors
from spellchecker import SpellChecker

print("-----------------------------------------------------------------------------")
print("---------------------------- Start api V18 premium --------------------------")
print("-----------------------------------------------------------------------------")

# logging
os.chdir(os.path.dirname(os.path.abspath(__file__)))
log_formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
log_handler = RotatingFileHandler('log.txt', mode='a', maxBytes=5 * 1024 * 1024, backupCount=7)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('ML')

logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
###################

t = str(datetime.now(timezone.utc))
print("start runtime: " + str(t))

PAGE_SIZE = 9
print("Loading shopping info from database ... ")

# pip3 install -U spacy
# python3 -m spacy download en_core_web_md

nlp = spacy.load('en_core_web_md')

# localhost is better in performance.
# The localhost has pipe comm without network stack.
cnx = mysql.connector.connect(user=config.mysql['user'], password=config.mysql['password'],
                              host=config.mysql['host'], database='new_db', port=3306)

cursor = cnx.cursor()
str_sql = 'SELECT parent_word, group_, shopping_id FROM new_db.shoppinglist_new'
cursor.execute(str_sql)
result = cursor.fetchall()
cnx.close()

# parent_word, group, shopping_id
base_dataset = {str(row[2]): [str(row[0]), str(row[1])] for row in result}

# {shopping_id: category}
g_categories_dict = {shopping_id: v[1] for shopping_id, v in base_dataset.items()}
g_categories_vector_dict = {shopping_id: nlp(' '.join([sub.lower() for sub in v])) for shopping_id, v in
                            base_dataset.items()}
g_categories_norm_vector_dict = {shopping_id: parse.vector / parse.vector_norm for shopping_id, parse in
                                 g_categories_vector_dict.items() if parse.vector_norm > 0}
g_categories_norm_vector_mat = np.array(list(g_categories_norm_vector_dict.values()))

zero_categories = [g_categories_dict[shopping_id] for shopping_id, parse in g_categories_vector_dict.items() if
                   parse.vector_norm == 0]
if len(zero_categories) > 0:
    print("##### Invalid categories #####\n", zero_categories)

print("Loading keywords from pkl and json ... ")

with open('Keywords/loc_keyword_biz.pkl', 'rb') as f:
    loc_keyword_biz = pickle.load(f)

with open('Keywords/organic_keyword_biz.pkl', 'rb') as f:
    organic_keyword_biz = pickle.load(f)

# Felix: Open later
org_key_fp = os.listdir('Keywords/organic_keywords')
organic_keywords = {}
for fp in org_key_fp:
    subset = pickle.load(open('Keywords/organic_keywords/{}'.format(fp), 'rb'))
    organic_keywords.update(subset)
del subset

spell_vocab = SpellChecker(local_dictionary='Keywords/spell_keyword_vocab.json')

with open('Keywords/spell_keyword_vocab.json', 'r') as f:
    spell_vocab_dict = json.load(f)
with open('Keywords/organic_keyword_vocab.json', 'r') as f:
    spell_org_dict = json.load(f)
with open('Keywords/loc_keyword_vocab.json', 'r') as f:
    spell_loc_dict = json.load(f)
with open('Keywords/town_keyword_vocab.json', 'r') as f:
    spell_town_dict = json.load(f)
with open('Keywords/organic_premium_keyword_biz.pkl', 'rb') as f:
    organic_premium_keyword_biz = pickle.load(f)
with open('Keywords/loc_premium_keyword_biz.pkl', 'rb') as f:
    loc_premium_keyword_biz = pickle.load(f)

# keyword: [0,0,0,0,0,0,1]   # keyword location pose probabilities
with open('Keywords/loc_keyword_prob.json', 'r') as f:
    loc_keyword_prob = json.load(f)

print("Loading town and business data from META_DATA_INDEX, au_towns ... ")

w2v = KeyedVectors.load_word2vec_format('Text Embedding/GloVe/W2V.50d.txt')
# mydict = corpora.Dictionary.load('Keywords/mydict')
# tfidf = TfidfModel.load('Keywords/tfidf')
# Felix: Not used mydict, tfidf
# mydict = pickle.load(open('Keywords/mydict', 'rb'))
# tfidf = pickle.load(open('Keywords/tfidf', 'rb'))

au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))
B_DATA = pickle.load(open('Keywords/business_keywords.pkl', 'rb'))
# premium_keywords = pickle.load(open('Keywords/premium_keywords.pkl', 'rb'))

TOWN_INFO = {}
for town_id, town_name, urban_area, postcode, state_code, lat, long, radius in zip(au_towns['id'], au_towns['name'],
                                                                                   au_towns['urban_area'],
                                                                                   au_towns['postcode'],
                                                                                   au_towns['state_code'],
                                                                                   au_towns['latitude'],
                                                                                   au_towns['longitude'],
                                                                                   au_towns['radius']):
    if lat is None or long is None:
        continue

    if radius is None:
        radius = 0

    TOWN_INFO[int(town_id)] = {"name": town_name, "urban_area": urban_area, "postcode": postcode,
                               "state_code": state_code,
                               "lat_lon": (float(lat), float(long)), "radius": float(radius)}

del au_towns
TOWN_INFO[0] = {"name": "Empty Town", "urban_area": "", "postcode": "", "state_code": "", "lat_lon": (0, 0),
                "radius": 0}


# integrated to stopwords
# ignored_keywords = ['near', 'nearest', 'in', 'at', 'around', 'within', 'here', 'someplace', 'somewhere']
# ignored_keywords_vec = [w2v[k] for k in ignored_keywords if k in w2v]

def extract_town(text):
    town_name_0, town_id_list = None, None
    town_set = None
    for n in range(3, 0, -1):
        combines = combinations(text, n)
        for combine in combines:
            for keyword in combine:
                # didn't match town
                t_arr = None
                match_town_keyword = helper.getMatchKeyword(spell_town_dict, keyword, 'upper')

                if match_town_keyword in spell_town_dict:
                    t_arr = set(spell_town_dict[match_town_keyword].keys())
                else:
                    temp = []
                    for tid, v in TOWN_INFO.items():
                        if v['postcode'] == keyword:
                            temp.append(tid)
                    if len(temp) > 0:
                        t_arr = set(temp)
                if town_set is None:
                    # {'113410'}
                    if t_arr is not None:
                        town_set = t_arr
                else:
                    if t_arr is not None:
                        # town_set = town_set.intersection(t_arr)
                        town_set = list(set(list(town_set) + list(t_arr)))
    if town_set is not None and len(town_set) > 0:
        town_name_0 = TOWN_INFO[int(list(town_set)[0])]['name']
        town_id_list = [int(tid) for tid in list(town_set)]
    return town_name_0, town_id_list


def loc_nearest_match(lat_lon=None):
    if lat_lon is None:
        lat_lon = (0, 0)
    nearest_town = ['', np.inf]
    for tid, v in TOWN_INFO.items():
        dist = helper.haversine(lat_lon, v['lat_lon']) - v['radius']
        if dist <= 0:
            nearest_town = [tid, dist]
            # Because return only one town in finally
            break
        elif dist < nearest_town[1]:
            nearest_town = [tid, dist]

    return nearest_town[0]


def get_location_from_levels(loc_query, all_loc_combines, loc_level_nums, non_loc_level, loc_level, tid):
    # not matched directly location keywords
    if loc_level == 0:
        location = str(TOWN_INFO[tid]['name'])
        if TOWN_INFO[tid]['state_code'] is not None:
            location = location + ' ' + TOWN_INFO[tid]['state_code']
    # matched directly location keywords
    else:
        # matched keyword positions tuple, (3, 2, 1)
        combine_tup = all_loc_combines[loc_level_nums - loc_level - 1]
        locs = {}
        for item in combine_tup:
            word = list(loc_query.keys())[item]
            # parsed location pose (integer 1-6)
            pose = loc_query[word]
            if pose == -1:
                continue
            locs[word] = pose
        locs = sorted(locs.items(), key=lambda x: x[1])
        location = ''
        # adding town name and urban_area_name
        for word, pose in locs:
            # no town and no state
            if pose != 6 and pose != 0:
                location = location + ' ' + word + ' ' + list(const.pose_keywords.keys())[6 - pose]

        location = location + ' ' + TOWN_INFO[tid]['name']
        if TOWN_INFO[tid]['state_code'] is not None:
            location = location + ' ' + TOWN_INFO[tid]['state_code']

    return location.strip()


def extract_loc(text, town_name_list, topN):
    non_loc_query = {}
    loc_query = {}
    last_loc_word = ''
    pop_words = []

    for word in text:
        if word in const.pose_keywords:
            if last_loc_word == '':
                continue
            loc_query[last_loc_word] = (const.pose_keywords[word], loc_query[last_loc_word][1])
            last_loc_word = ''
            continue

        pl_word = helper.getPlural(word)
        sl_word = helper.getSingular(word)
        if spell_vocab.unknown([word]) and pl_word is not None and spell_vocab.unknown([pl_word]) \
                and sl_word is not None and spell_vocab.unknown([sl_word]):
            word = spell_vocab.correction(word)

        match_non_loc_keyword = helper.getMatchKeyword(spell_vocab_dict, word, 'lower')
        if match_non_loc_keyword is not None:
            words = [match_non_loc_keyword]
        else:
            words = []

        for word1 in words:
            if word1 in spell_org_dict:
                # if word not in spell_loc_dict or (word in spell_loc_dict and spell_org_dict[word] >=
                # spell_loc_dict[word]):
                non_loc_query[word1.upper()] = spell_org_dict[word1]
                # if word is also loc, its priority change to lower.
                if word1 in spell_loc_dict:
                    non_loc_query[word1.upper()] -= (spell_loc_dict[word1] * 10)

            if word1.upper() in const.populate_search_words:
                pop_words.append(word1.upper())

            match_loc_keyword = helper.getMatchKeyword(spell_loc_dict, word1, 'lower')
            if match_loc_keyword in spell_loc_dict:
                if word1 not in spell_org_dict or \
                        (word1 in spell_org_dict and spell_loc_dict[match_loc_keyword] > spell_org_dict[word1]):
                    '''
                    # max prob => pose (but it can't search in other pose)
                    pose, prob, inx = -1, -1, 0
                    for p in loc_keyword_prob[word.upper()]:
                        if p > 0 and prob <= p:
                            pose = inx
                        inx += 1
                    '''

                    pose = -1
                    # only one prob and prob = 1 => pose
                    if len([prob for prob in loc_keyword_prob[word1.upper()] if prob > 0]) == 1:
                        for prob in loc_keyword_prob[word1.upper()]:
                            pose += 1
                            if prob > 0:
                                break
                    # prob = 1 => pose (important: didn't searched in other pose)
                    else:
                        inx = 6
                        for prob in loc_keyword_prob[word1.upper()][::-1]:
                            if prob == 1:
                                pose = inx
                                break
                            inx -= 1

                    loc_query[word1.upper()] = (pose, spell_loc_dict[word1])
                    last_loc_word = word1.upper()
    _non_loc_query = sorted(non_loc_query.items(), key=lambda x: x[1], reverse=True)

    _loc_query = sorted(loc_query.items(), key=lambda x: x[1])
    _loc_query = {item[0]: item[1][0] for item in _loc_query}
    # if only non_loc is enough for topN, remove both keywords.
    non_loc_query = []
    for word, score in _non_loc_query:
        non_loc_query.append(word)
        # only non-loc keywords is all appended.
        # if meaningful non-loc+loc also is appended.
        # Felix: Only if non_loc_keyword is in loc_query
        if len(non_loc_query) > 1 and word.upper() in loc_query and spell_org_dict[word.lower()] < topN \
                and word.lower() in spell_loc_dict:
            # reach predicted
            non_loc_query = non_loc_query[:-1]
            break
    # if loc keyword is in non_loc_query, pop the keyword
    loc_query = {k: v for k, v in _loc_query.items() if k not in non_loc_query}
    # if input is one, consider only as non-location
    if len(text) == 1 and len(loc_query) == 1 and len(non_loc_query) == 1:
        loc_query = {}

    # In loc keywords, town keywords change to 6 (town pose)
    if town_name_list is not None:
        town_name_keywords = town_name_list.split()
        loc_query = {k: 6 if k in town_name_keywords else pose for k, pose in loc_query.items()}

    # empty non-loc is the same as in populated keywords
    if len(non_loc_query) == 0 and len(pop_words) > 0:
        non_loc_query = pop_words

    return non_loc_query, loc_query


def extract(query, lat_lon=None, param_radius=40000, topN=1000, page=1, showPrint=False):
    # print("Start extract ... ")
    if lat_lon is None:
        lat_lon = []
    ori_start = None
    last_result = {}
    t0, t1, t2, t3, t4 = [], [], [], [], []
    # target_b = 1448910
    # If not test, please set target_b to None
    target_b = None
    target_result = {}
    try:

        # EXTRACT NUMBERS FROM TEXT
        t_start = time()
        ori_start = t_start
        ori_query = query

        # REMOVE COMMON WORDS FROM QUERY (stop_key, ignore_key, one_char)
        query = ''.join([c for c in query if c.isalnum() or c == ' '])
        query = [w.strip() for w in query.split()]
        query = [w for w in query if w.lower() not in const.stopwords and len(w) > 1]

        query_in_w2v = [w for w in query if w.lower() in w2v]
        query_not_in_w2v = [w for w in query if w.lower() not in w2v]

        # query_in_w2v = [w for w in query_in_w2v
        #                if max(w2v.cosine_similarities(w2v[w.lower()], ignored_keywords_vec)) < 0.7]

        query_extracted = query_in_w2v + query_not_in_w2v

        t0 = ['remove stop keywords from text', time() - t_start, query_extracted]

        # EXTRACT TOWN FROM QUERY
        t_start = time()

        query_preproc = [const.loc_keyword_pose[keyword] if keyword in const.loc_keyword_pose else keyword for keyword
                         in query_extracted]
        # Extract town info from location keywords
        loc_town_name, loc_town_id_list = extract_town(query_preproc)

        if showPrint:
            print('loc_town_name', loc_town_name)
            print('loc_town_id_list', loc_town_id_list)

        non_loc_query, loc_query = extract_loc(query_preproc, town_name, topN)
        if showPrint:
            print('extract_loc non_loc_query', non_loc_query)
            print('extract_loc loc_query', loc_query)
        # If non-loc is empty, try to use ignored keywords.
        # DR = DOCTOR
        if len(non_loc_query) == 0:
            if 'DR' in query_extracted:
                non_loc_query.append('DOCTOR')

        # if input is directly town, start_town is just it.
        best_matched_town_lat_lon, best_matched_town_id = None, 0

        if len(lat_lon) > 0 and lat_lon[0] != (None, None) and loc_town_name is not None:
            distance = param_radius
            # distance = 40000
            for tid in loc_town_id_list:
                temp_dist = helper.haversine(lat_lon[0], TOWN_INFO[tid]['lat_lon']) - TOWN_INFO[tid]['radius']
                # print(TOWN_INFO[tid]['name'], TOWN_INFO[tid]['state_code'],
                #       'Distance', helper.haversine(lat_lon[0], TOWN_INFO[tid]['lat_lon']),
                #       'Radius', TOWN_INFO[tid]['radius'], 'Distance-Radius', temp_dist)
                if temp_dist < distance:
                    best_matched_town_id = tid
                    best_matched_town_lat_lon = TOWN_INFO[tid]['lat_lon']
                    if temp_dist < 0:
                        break
                    distance = temp_dist
            if showPrint:
                print('best_matched_town', best_matched_town_id, TOWN_INFO[best_matched_town_id]['name'])
        # loc_query:  {keyword: pose}

        # not exist town keyword
        if const.pose_keywords['TOWN'] not in loc_query.values() and len(lat_lon) != 0:
            if best_matched_town_lat_lon is not None:
                tid = best_matched_town_id
            else:
                tid = loc_nearest_match(lat_lon[0])
            if showPrint:
                print('nearest town', TOWN_INFO[tid]["name"])

            loc_query_town = {
                helper.getMatchKeyword(spell_loc_dict, word, 'upper')
                if helper.getMatchKeyword(spell_loc_dict, word, 'upper') is not None
                else spell_vocab.correction(word).upper():
                    const.pose_keywords['TOWN'] for word in (TOWN_INFO[tid]["name"].split())
            }

            if TOWN_INFO[tid]["state_code"] is not None and len(TOWN_INFO[tid]["state_code"]) > 0:
                loc_query_town.update({
                    helper.getMatchKeyword(spell_loc_dict, word, 'upper')
                    if helper.getMatchKeyword(spell_loc_dict, word, 'upper') is not None
                    else spell_vocab.correction(word).upper():
                        const.pose_keywords['STATE'] for word in (TOWN_INFO[tid]["state_code"].split())
                })

            # user lat_lon town is the lowest priority
            loc_query_town.update(loc_query)
            loc_query = loc_query_town

        t1 = ['extract loc or nearest loc from query', "town name:", loc_town_name, "non-loc:", non_loc_query, "loc:",
              loc_query, time() - t_start]

        t_start = time()
        t2 = ['extract business keywords from query and mis-spell processed', non_loc_query, time() - t_start]

        if len(lat_lon) > 0:
            t2.append(["determine town's lat_lon", lat_lon, time() - t_start])

        # town_name = 'CLOVELLY'
        # town_id_list = [2906, 2907, 111230]
        # non_loc_query = ['PLUMBER']
        # loc_query = {'EASTLAKE': 6, 'NSW': 0}

        if showPrint:
            print('non_loc_query', non_loc_query)
            print('loc_query', loc_query)

        # POOL & SORT BUSINESSES
        if len(lat_lon) == 0:
            lat_lon = [(None, None)]
        # Only handle first element lat_lon[0], So don't use lat_lon[1], lat_lon[2], ...
        param_lat_lon = lat_lon[0]

        # POOL BUSINESS (c_dist, h_dist)
        # Here make biz_pool_c with proper c_dist, h_dist value
        if 1:
            t_start = time()

            non_loc_keys = len(non_loc_query)

            b_non_loc_list = []
            for key_pos in range(non_loc_keys):
                b_non_loc_list.append({})
            idx = 0
            # non-loc keywords is preferred in order, Low index is high score
            # ONLY NON_LOC_LIST, low index is high score, all others is HIGH-INDEX = HIGH SCORE
            for word in non_loc_query:
                if word in organic_keyword_biz:
                    b_non_loc_list[idx] = organic_keyword_biz[word]
                    # print(word, len(organic_keyword_biz[word]))
                idx += 1
            # print('1448903', b_non_loc_list[0][1448903])
            t3.append(["non-loc biz candidates.", time() - t_start])
            t_start = time()

            loc_keys = len(loc_query)

            non_loc_level_nums = 2 ** non_loc_keys - 1
            loc_level_nums = 2 ** loc_keys
            premium_level_nums = 3
            # demo = 2, premium = 1,  non-premium = 0
            # rank1: demo, rank2: premium, rank3: non

            # --------------------- RESULT 1 (non loc level) ----------------------------
            result_12 = {}
            topN_reached = False
            target_reached = False
            if target_b is None:
                target_reached = True
            picked_count = 0

            for non_loc_level in range(non_loc_level_nums):
                result_12[non_loc_level] = {}

            # (0, 1, 2), (0, 1), (0, 2), (1, 2) ...
            all_non_loc_combines = []
            for n in range(non_loc_keys, 0, -1):
                all_non_loc_combines += list(combinations(range(non_loc_keys), n))

            all_loc_combines = []
            for n in range(loc_keys, 0, -1):
                all_loc_combines += tuple(combinations(range(loc_keys - 1, -1, -1), n))

            # (3, 2, 1): 7 ...
            all_loc_combine_table = {(()): 0}
            idx = loc_level_nums - 1
            for tup in all_loc_combines:
                all_loc_combine_table[tup] = idx
                idx -= 1

            duplicate_check = {}
            # ------------------------------ Start for non_loc_level -----------------------------
            # print('Start for non_loc_level')
            for non_loc_level in range(non_loc_level_nums):
                # each non_loc_level processing
                non_loc_key_combines = all_non_loc_combines[non_loc_level]
                non_loc_level = non_loc_level_nums - non_loc_level - 1

                # -------------------------- RESULT 2 (loc level) ---------------------------
                # result_2 init, result_2 = result_12[non_loc_level]

                for loc_level in range(loc_level_nums):
                    # result_12[non_loc_level].append({})
                    result_12[non_loc_level][loc_level] = {}

                # avoid populate keywords
                if len(non_loc_key_combines) == 1 and \
                        non_loc_query[non_loc_key_combines[0]] in const.populate_search_words:
                    if len(non_loc_query) > 1:
                        continue
                # Integrate b_non_loc_list elements by
                b_non_loc_list_all = []
                duplicate_check_all = {}
                for idx in non_loc_key_combines:
                    for b in b_non_loc_list[idx]:
                        if b in duplicate_check:
                            continue
                        b_non_loc_list_all.append(b)
                        duplicate_check_all[b] = ''
                        # print(B_DATA[b][2])
                        # if B_DATA[b][2] == '14996':
                        #     print("HERE", b)
                        # if B_DATA[b][2] == '15287':
                        #     print("HERE", b)
                        # if B_DATA[b][2] == '103187':
                        #     print("HERE", b)

                # print(b_non_loc_list_all)
                # print('non_loc_key_combines', non_loc_key_combines[-1])
                # print(b_non_loc_list[non_loc_key_combines[-1]])
                # Felix: why use -1 for last element in non_loc_key_combines? Is it just the highest order?
                # If Low index is high score in non-loc keywords, should 0, the lowest order
                # for b in b_non_loc_list[non_loc_key_combines[0]]:
                # cnt = 0
                # for b in b_non_loc_list[non_loc_key_combines[-1]]:

                for b in b_non_loc_list_all:
                    #     if cnt == 0:
                    #         print(b)
                    # cnt += 1
                    if b in duplicate_check:
                        continue
                    ok = True
                    # for key_pos in non_loc_key_combines[:-1]:
                    #     if b not in b_non_loc_list[key_pos]:
                    #         ok = False
                    #         break

                    if ok:
                        # get loc level
                        # 0: all country
                        loc_prob_score = 0
                        key_pos = 0
                        loc_key_combines = ()
                        for keyword, pose in loc_query.items():
                            loc_biz_list = loc_keyword_biz[helper.getMatchKeyword(loc_keyword_biz, keyword, 'upper')]
                            if b in loc_biz_list:
                                if pose == -1:
                                    loc_key_combines = (key_pos,) + loc_key_combines
                                    for prob in loc_biz_list[b][::-1]:
                                        if prob > 0:
                                            loc_prob_score += prob
                                            break
                                elif loc_biz_list[b][pose] > 0:
                                    loc_key_combines = (key_pos,) + loc_key_combines
                                    loc_prob_score += loc_biz_list[b][pose]
                                    # print(b, keyword, loc_key_combines)
                            key_pos += 1
                        loc_level = all_loc_combine_table[loc_key_combines]

                        picked_count += 1
                        duplicate_check[b] = ''
                        if picked_count >= topN + 200:  # For relevant location clarify
                            # don't break, cause of h_dist need to finish currently search of biz level
                            topN_reached = True
                        if b == target_b:
                            target_reached = True

                        # ---------------------------- RESULT 3 (loc probability level) ---------------------------
                        # print('---------------- Start loc probability level -----------------')

                        loc_prob_level = loc_prob_score
                        if loc_prob_level not in result_12[non_loc_level][loc_level]:
                            result_12[non_loc_level][loc_level][loc_prob_level] = {}

                        # avoid populate keywords
                        # Felix: need to check more this level part

                        # if len(loc_key_combines) == 1 and keyword in const.populate_search_words:
                        #     continue
                        if len(loc_key_combines) == 1 and \
                                list(loc_query.keys())[loc_key_combines[0]] in const.populate_search_words:
                            continue
                        if len(loc_key_combines) == 2 and \
                                list(loc_query.keys())[loc_key_combines[1]] in const.populate_search_words and \
                                (list(loc_query.values())[loc_key_combines[0]] == 0
                                 or list(loc_query.values())[loc_key_combines[0]] == 5):
                            continue

                        # ---------------------------- RESULT 4 (premium level) -------------------------
                        # it is level but it is score and key.
                        # premium has no keyword orders.

                        # print('---------------- Start premium level -----------------')

                        premium_level = 0

                        for keyword in non_loc_query:
                            # if keyword in organic_premium_keyword_biz:
                            #     print(keyword)
                            #     print(b)
                            #     print(organic_premium_keyword_biz[keyword])
                            # # LEAKE
                            # # 162331, 227817, 331433, 657834, ....
                            # # {1448903: [None]}
                            # if b in organic_premium_keyword_biz['MECHANIC']:
                            #     # print(keyword)
                            #     print(b)
                            #     # print(organic_premium_keyword_biz[keyword])

                            if keyword in organic_premium_keyword_biz and b in organic_premium_keyword_biz[keyword]:
                                premium_level += const.PREMIUM_BIZ_SCORE
                                # print('PREMIUM_BIZ_SCORE', keyword, premium_level)

                                if organic_premium_keyword_biz[keyword] == 1:  # premium
                                    premium_level += const.PREMIUM_PREM_SCORE
                                    # print('PREMIUM_PREM_SCORE', keyword, premium_level)
                                elif organic_premium_keyword_biz[keyword] == 2:  # demonstrate
                                    premium_level += const.PREMIUM_DEMO_SCORE
                                    # print('PREMIUM_DEMO_SCORE', keyword, premium_level)

                        for keyword in loc_query:
                            if keyword in loc_premium_keyword_biz and b in loc_premium_keyword_biz[keyword]:
                                premium_level += const.PREMIUM_LOC_SCORE
                                # print('PREMIUM_LOC_SCORE', keyword, premium_level)

                                if loc_premium_keyword_biz[keyword] == 1:  # premium
                                    premium_level += const.PREMIUM_PREM_SCORE
                                    # print('PREMIUM_PREM_SCORE', keyword, premium_level)
                                elif loc_premium_keyword_biz[keyword] == 2:  # demonstrate
                                    premium_level += const.PREMIUM_DEMO_SCORE
                                    # print('PREMIUM_DEMO_SCORE', keyword, premium_level)

                        if premium_level not in result_12[non_loc_level][loc_level][loc_prob_level]:
                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level] = {}

                        # --------------------------- RESULT 5 (town level) --------------------------
                        # print('---------------- Start town level -----------------')
                        # [non_loc_level][
                        # loc_level]["premium_level"]["town_id"]{"town_dist":dist, "biz":{bid:h_dist}}

                        if b in B_DATA and B_DATA[b][2] is not None:
                            townID = B_DATA[b][2]
                        else:
                            townID = 0

                        if townID not in result_12[non_loc_level][loc_level][loc_prob_level][premium_level]:
                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level][townID] = {}

                            # if there is no position, use first town position instead of it.
                            if param_lat_lon == (None, None):
                                param_lat_lon = TOWN_INFO[townID]["lat_lon"]
                                t3 = ["determine town's lat_lon", param_lat_lon, time() - t_start]
                            # Felix: Why town_dist can be negative value? i.e. -1.3
                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level][townID]["town_dist"] = \
                                helper.haversine(TOWN_INFO[townID]["lat_lon"], param_lat_lon) \
                                - TOWN_INFO[townID]["radius"]

                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level][townID]["biz"] = {}
                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level][townID]["biz"][b] = \
                                helper.haversine(B_DATA[b][1], param_lat_lon)
                        else:
                            result_12[non_loc_level][loc_level][loc_prob_level][premium_level][townID]["biz"][b] = \
                                helper.haversine(B_DATA[b][1], param_lat_lon)

                # currently, non_loc_level search end
                if topN_reached and target_reached:
                    break
            # ------------------------------ End for non_loc_level -----------------------------
            # print('End for non_loc_level')
            t3.append(["non-loc biz search end. Picked biz:", picked_count, time() - t_start])
            t_start = time()
            _t4 = []

            # initialize
            topN_reached = False
            target_reached = False
            after_relevant_got = False
            if target_b is None:
                target_reached = True
            STOP_non_loc_level, STOP_loc_level, STOP_town_id = None, None, None
            AFTER_non_loc_level, AFTER_loc_level, AFTER_town_id, AFTER_counts = None, None, None, None
            # biz_pool_C_All: {b:[c_dist, p_dist, h_dist, town_id, non_loc_level, loc_level, loc_prob_level]}
            biz_pool_C_All = {}

            # print('Start making biz_pool_C_All')

            for non_loc_level in range(non_loc_level_nums):
                non_loc_level = non_loc_level_nums - non_loc_level - 1
                # print('non_loc_level', non_loc_level)
                # print('non_loc_level_nums', non_loc_level_nums)
                if len(result_12[non_loc_level]) == 0:
                    continue
                c_dist = (non_loc_level + 2) / (non_loc_level_nums + 1)
                # if c_dist != 1:
                # print('c_dist', c_dist)

                for loc_level in range(loc_level_nums):
                    loc_level = loc_level_nums - loc_level - 1

                    if len(result_12[non_loc_level][loc_level]) == 0:
                        continue
                    # print('loc_level')
                    # print(result_12[non_loc_level][loc_level])

                    result_3 = sorted(result_12[non_loc_level][loc_level].items(), key=lambda x: x[0], reverse=True)
                    if len(result_3) == 0:
                        continue
                    # print('result_3')
                    # print(result_3)

                    for (loc_prob_level, result_4) in result_3:
                        # Felix: Sorted by premium_level
                        result_4 = sorted(result_4.items(), key=lambda x: x[0], reverse=True)
                        if len(result_4) == 0:
                            continue
                        # print('result_4')
                        # print(result_4)

                        for (premium_level, result_5) in result_4:
                            # ------------------------------- RESULT 6 (h_dist level) --------------------------

                            # town_dist, start_town is first picked town (if town is not inputted)
                            if best_matched_town_lat_lon is None:
                                result_5 = sorted(result_5.items(), key=lambda x: x[1]["town_dist"])
                                first_tid = result_5[0][0]
                                best_matched_town_lat_lon = TOWN_INFO[first_tid]["lat_lon"]
                                best_matched_town_id = first_tid
                            else:
                                towns = result_5.keys()
                                for tid in towns:
                                    result_5[tid]['town_dist'] = \
                                        helper.haversine(TOWN_INFO[tid]["lat_lon"], best_matched_town_lat_lon) \
                                        - TOWN_INFO[tid]["radius"]
                                result_5 = sorted(result_5.items(), key=lambda x: x[1]["town_dist"])

                            # print('result_5')
                            # print(result_5)
                            for (tid, result_6) in result_5:

                                if STOP_town_id is not None and \
                                        (STOP_town_id != tid or STOP_loc_level != loc_level
                                         or STOP_non_loc_level != non_loc_level):
                                    AFTER_non_loc_level, AFTER_loc_level, AFTER_town_id = non_loc_level, loc_level, tid
                                    AFTER_counts = len(result_6['biz'])
                                    after_relevant_got = True
                                    break

                                if not topN_reached or not target_reached:
                                    town_dist = result_6["town_dist"]
                                    result_6 = sorted(result_6['biz'].items(), key=lambda x: x[1])
                                    # print('result_6')
                                    # print(result_6)
                                    # print(c_dist + premium_level / 100000)
                                    # biz_pool_C_All Structure
                                    # {b:[c_dist, p_dist, h_dist, town_id, non_loc_level, loc_level, loc_prob_level]}
                                    biz_pool_C_All.update({b: [c_dist + premium_level / 100000,
                                                               premium_level, h_dist, tid, town_dist,
                                                               non_loc_level, loc_level, loc_prob_level,
                                                               best_matched_town_id]
                                                           for (b, h_dist) in result_6
                                                           if h_dist < param_radius
                                                           })
                                    if target_b is not None:
                                        for b, h_dist in result_6:
                                            if b == target_b:
                                                print('target_reached', b)
                                                target_reached = True
                                                break
                                    # for b, h_dist in result_6:
                                    #     print(non_loc_level, loc_level, round(loc_prob_level, 2), premium_level,
                                    #           round(h_dist, 2), tid, round(town_dist, 2))
                                    # print(best_matched_town_id)
                                    if len(biz_pool_C_All) >= topN and target_reached:
                                        topN_reached = True
                                        STOP_non_loc_level, STOP_loc_level, STOP_town_id = non_loc_level, loc_level, tid
                                        # break
                                    # print("End for: " + str(len(biz_pool_C_All)))

                            if topN_reached and target_reached and after_relevant_got:
                                break
                        if topN_reached and target_reached and after_relevant_got:
                            break
                    if topN_reached and target_reached and after_relevant_got:
                        break
                if topN_reached and target_reached and after_relevant_got:
                    break
            # print('biz_pool_C')
            biz_pool_C = {}
            idx = 0
            for b, v in biz_pool_C_All.items():
                biz_pool_C[b] = v
                idx += 1
                if idx == topN:
                    break
            # print(len(biz_pool_C))
            _t4.append(["pool c_dist, p_dist, h_dist via quick search. sorted final results:", len(biz_pool_C),
                        time() - t_start])

        if len(biz_pool_C) == 0:
            # Time Log into Difference
            time_log = [t0, t1, t2, t3, _t4]
            return {"result": {}, "status": "not found", "time_log": time_log, "total_time": time() - ori_start}

        # PREMIUM SUBSET FROM BIZ_POOL_H
        # t_start = time()
        # prem_subset = {b: premium_keywords[b] for b in biz_pool_C if b in premium_keywords}
        #
        # _t4.append(["premium subset based on biz_pool_ALL", time() - t_start])
        # print("premium subset:", time() - t_start, len(prem_subset))

        # INCLUDE BUSINESS BASED ON PREMIUM S2
        # if len(loc_query) > 0:
        #     t_start = time()
        #     # Felix: get biz_pool_S2
        #     S2_matched = {b: helper.list_intersect(set(loc_query), dic['S2']) for b, dic in prem_subset.items()}
        #     biz_pool_S2 = {b: l for b, l in S2_matched.items() if len(l) != 0}
        #
        #     _t4.append(["use town to determine biz_pool_S2", time() - t_start])
        #     # print("S2 subset:", time() - t_start, len(biz_pool_S2))
        # else:
        #     t_start = time()
        #     biz_pool_S2 = {}
        #     _t4.append(["no town found - empty biz_pool_S2", time() - t_start])

        # INCLUDE BUSINESS BASED ON PREMIUM T3
        t_start = time()

        query_set = set(non_loc_query)
        # T3_matched = {b: helper.list_intersect(query_set, dic['T3']) for b, dic in prem_subset.items()}
        # biz_pool_T3 = {b: l for b, l in T3_matched.items() if len(l) != 0}
        #
        # _t4.append(["use query to determine biz_pool_T3", time() - t_start])
        # print("T3 subset:", time() - t_start, len(biz_pool_T3))

        # INCLUDE BUSINESS BASED ON BUSINESS NAME
        t_start = time()

        biz_pool_NAME = {b: [helper.list_intersect(query_set, B_DATA[b]), B_DATA[b]]
                         for b in biz_pool_C}

        _t4.append(["use query to determine biz_pool_NAME", time() - t_start])

        t_start = time()

        # s2_result = biz_pool_S2
        # t3_result = biz_pool_T3

        name_result = {}
        organic_result = {}
        cnt = 1
        top_locations = []  # all top location lists, so can use topN, also.
        base_non_loc_level, base_loc_level, base_loc_prob_level, base_town_id = -1, -1, -1, -1
        total_page_count = (len(biz_pool_C) + 2) // PAGE_SIZE + 1

        print('---------------- Organic Result -------------------')

        for i, b in enumerate(biz_pool_C):
            if base_loc_level != biz_pool_C[b][6] or base_non_loc_level != biz_pool_C[b][5] or base_town_id != \
                    biz_pool_C[b][3]:
                base_non_loc_level = biz_pool_C[b][5]
                base_loc_level = biz_pool_C[b][6]
                # base_loc_prob_level = biz_pool_C[b][7]
                base_town_id = biz_pool_C[b][3]

                location = get_location_from_levels(loc_query, all_loc_combines, loc_level_nums, base_non_loc_level,
                                                    base_loc_level, base_town_id)

                top_locations.append(
                    [location, 1, helper.haversine(TOWN_INFO[biz_pool_C[b][3]]['lat_lon'], param_lat_lon) -
                     TOWN_INFO[biz_pool_C[b][3]]['radius']]
                )
            else:
                # picked business counting
                top_locations[-1][1] += 1

            if b == target_b:
                target_result['bid'] = b
                target_result['business_name'] = B_DATA[b][0] if b in B_DATA else ''
                target_result['c_dist'] = biz_pool_C[b][0]
                target_result['p_dist'] = biz_pool_C[b][1]
                target_result['h_dist'] = biz_pool_C[b][2]
                target_result['town_id'] = biz_pool_C[b][3]
                target_result['town_name'] = TOWN_INFO[biz_pool_C[b][3]]['name']
                target_result['state_code'] = TOWN_INFO[biz_pool_C[b][3]]['state_code']
                target_result['town_radius'] = TOWN_INFO[biz_pool_C[b][3]]['radius']
                target_result['town_dist'] = biz_pool_C[b][4]
                target_result['non_loc_level'] = biz_pool_C[b][5]
                target_result['loc_level'] = biz_pool_C[b][6]
                target_result['loc_prob_level'] = biz_pool_C[b][7]
                target_result['start_town_name'] = TOWN_INFO[biz_pool_C[b][8]]['name']

            page_number = (i + 1) // PAGE_SIZE + 1
            if page_number != page:
                continue

            organic_result[str(cnt)] = {}
            # organic_result[str(cnt)]['c_dist'] = min(1, 2 * biz_pool_C[b][0] / (len(query) + 0.01))
            organic_result[str(cnt)]['bid'] = b
            organic_result[str(cnt)]['business_name'] = B_DATA[b][0] if b in B_DATA else ''
            organic_result[str(cnt)]['c_dist'] = biz_pool_C[b][0]
            organic_result[str(cnt)]['p_dist'] = biz_pool_C[b][1]
            organic_result[str(cnt)]['h_dist'] = biz_pool_C[b][2]
            organic_result[str(cnt)]['town_id'] = biz_pool_C[b][3]
            organic_result[str(cnt)]['town_name'] = TOWN_INFO[biz_pool_C[b][3]]['name']
            organic_result[str(cnt)]['state_code'] = TOWN_INFO[biz_pool_C[b][3]]['state_code']
            organic_result[str(cnt)]['town_radius'] = TOWN_INFO[biz_pool_C[b][3]]['radius']
            organic_result[str(cnt)]['town_dist'] = biz_pool_C[b][4]
            organic_result[str(cnt)]['non_loc_level'] = biz_pool_C[b][5]
            organic_result[str(cnt)]['loc_level'] = biz_pool_C[b][6]
            organic_result[str(cnt)]['loc_prob_level'] = biz_pool_C[b][7]
            organic_result[str(cnt)]['start_town_name'] = TOWN_INFO[biz_pool_C[b][8]]['name']
            # Felix: For reduce memory occupy, close this line. open later.
            organic_result[str(cnt)]['organic_html'] = organic_keywords[b]

            # if showPrint:
            print(organic_result[str(cnt)]['business_name'], organic_result[str(cnt)]['c_dist'],
                  organic_result[str(cnt)]['p_dist'], [round(organic_result[str(cnt)]['h_dist'], 2)],
                  organic_result[str(cnt)]['town_name'], organic_result[str(cnt)]['state_code'],
                  organic_result[str(cnt)]['non_loc_level'], organic_result[str(cnt)]['loc_level'],
                  round(organic_result[str(cnt)]['loc_prob_level'], 3),
                  organic_result[str(cnt)]['start_town_name'])

            '''
            organic_result[str(cnt)]['S2_matched'] = []
            organic_result[str(cnt)]['pimpt_S2'] = 0
            if b in s2_result:
                organic_result[str(cnt)]['S2_matched'] = s2_result[b]
                organic_result[str(cnt)]['pimpt_S2'] = len(s2_result[b])

            organic_result[str(cnt)]['T3_matched'] = []
            organic_result[str(cnt)]['pimpt_T3'] = 0
            if b in t3_result:
                organic_result[str(cnt)]['T3_matched'] = t3_result[b]
                organic_result[str(cnt)]['pimpt_T3'] = len(t3_result[b])
            '''
            # Felix: what's this?
            # if organic_result[str(cnt)]['c_dist'] >= 100:
            if organic_result[str(cnt)]['c_dist'] >= 1:
                organic_result[str(cnt)]['premium'] = 1
            else:
                organic_result[str(cnt)]['premium'] = 0

            # organic_result[str(cnt)]['NAME_matched'] = []
            # organic_result[str(cnt)]['pimpt_NAME'] = 0
            if b in name_result:
                organic_result[str(cnt)]['NAME_matched'] = name_result[b]
                organic_result[str(cnt)]['pimpt_NAME'] = len(name_result) / len(name_result[b])

            name_result[b] = biz_pool_NAME[b]

            cnt += 1

        # target result
        if target_b is not None and showPrint:
            print('---------------- Target Result -------------------')
            if target_result != {}:
                print(target_result['business_name'], target_result['c_dist'], target_result['p_dist'],
                      [round(target_result['h_dist'], 2)], target_result['town_name'], target_result['state_code'],
                      target_result['non_loc_level'], target_result['loc_level'],
                      round(target_result['loc_prob_level'], 3), target_result['start_town_name'])
            else:
                print('Not reached at the target')

        most_locations = sorted(top_locations, key=lambda x: x[1], reverse=True)
        top_location1 = [top_locations[0][0], top_locations[0][2]] if len(top_locations) > 0 else ""
        top_location2 = [most_locations[0][0], most_locations[0][1]] if len(most_locations) > 0 else ""
        top_location3 = [get_location_from_levels(loc_query, all_loc_combines, loc_level_nums, AFTER_non_loc_level,
                                                  AFTER_loc_level, AFTER_town_id),
                         AFTER_counts] if AFTER_town_id is not None else ""

        if top_location1 == "":
            resend_query1 = ""
        else:
            resend_query1 = top_location1[0].split()
            resend_query1_non_loc = [keyword for keyword in non_loc_query if keyword not in resend_query1]
            resend_query1 += resend_query1_non_loc
            resend_query1 = ' '.join(resend_query1)

        if top_location2 == "":
            resend_query2 = ""
        else:
            resend_query2 = top_location2[0].split()
            resend_query2_non_loc = [keyword for keyword in non_loc_query if keyword not in resend_query2]
            resend_query2 += resend_query2_non_loc
            resend_query2 = ' '.join(resend_query2)

        if top_location3 == "":
            resend_query3 = ""
        else:
            resend_query3 = top_location3[0].split()
            resend_query3_non_loc = [keyword for keyword in non_loc_query if keyword not in resend_query3]
            resend_query3 += resend_query3_non_loc
            resend_query3 = ' '.join(resend_query3)

        _result = {"Total_Page_Count": total_page_count, "Name": name_result, "Organic": organic_result,
                   "Top_Location1": top_location1, "Top_Location2": top_location2, "Top_Location3": top_location3,
                   "resend_query1": resend_query1, "resend_query2": resend_query2, "resend_query3": resend_query3}

        # For memory lack, remove name_result
        # _result = {"Total_Page_Count": total_page_count, "Name": 'name_result', "Organic": organic_result,
        #            "Top_Location1": top_location1, "Top_Location2": top_location2, "Top_Location3": top_location3,
        #            "resend_query1": resend_query1, "resend_query2": resend_query2, "resend_query3": resend_query3}

        # print('suburb_found', loc_query)
        query_info = {"query_made": ori_query, "lat_lon_queried": param_lat_lon, "suburb_found": loc_query}
        last_result = {'info': query_info, 'set': _result}

        _t4.append(["normalize dictionaries > dataframe > json", time() - t_start])

        # Finish log
        t4.append(_t4)

        # print("END:", time() - t_start)

        # DB Pool Cursor close
        # cursor.close()
        # connection_object.close()

        # Time Log into Difference
        time_log = [t0, t1, t2, t3, t4]

        print("---------------------- End Result ----------------------------")

        return {"result": last_result, "status": "success", "time_log": time_log, "total_time": time() - ori_start}
    except Exception as e:
        print("---------------------- Exception ----------------------------")
        print(e)
        # exit(1)
        if 't0' not in locals():
            t0 = ['t0', -1]
        if 't1' not in locals():
            t1 = ['t1', -1]
        if 't2' not in locals():
            t2 = ['t2', -1]
        if 't3' not in locals():
            t3 = ['t3', -1]
        if 't4' not in locals():
            t4 = [['t4', -1]]

        time_log = [t0, t1, t2, t3, t4]
        return {"result": {}, "status": "error", "exception": helper.PrintException(), "time_log": time_log,
                "total_time": time() - ori_start}


# Once only one execute, org_key_vec is cached in CPU cache
# It is very important for performance.
# If this is not called, will be decrease each first search time.

# a = extract('GAS FITTER 2035', [(-33.8670207, 151.2173064)], 20, 1000, 1, True)
# a = extract('LEAKS KINGSFORD', [(-33.8670207, 151.2173064)], 200, 1000, 1, True)
# a = extract('PLUMBER 2032', [(-33.8670207, 151.2173064)], 20, 1000, 1, True)
# a = extract('MOBILE MECHANIC CLOVELLY', [(-33.8670207, 151.2173064)], 20, 1000, 1, True)
# a = extract('jb hi fi', [(-33.8670207, 151.2173064)], 20, 1000, 1, True)
# a = extract('HOT WATER PLUMBER 2032', [(-33.8670207, 151.2173064)], 20, 1000, 1, True)
# a = extract('PET CARE NORTHBRIDGE', [(-33.8670207, 151.2173064)], 1000, 1, True)
# a = extract('FOOD TAKEOUTS', [(33.766, 151.243)], 1000, 1, True)
# a = extract('FOOD TAKEOUTS WYNYARD', [(-33.920, 151.243)], 20, 1000, 1, True)
a = extract('PLUMBERS EASTLAKES', [(-33.868112, 151.22349)], 40, 1000, 1, True)

# TOOTH FILLING DACEYVILLE, CHIPPED TOOTH DACEYVILLE, TOOTH FILLING KINGSFORD, CHIPPED TOOTH KINGSFORD,
# DENTAL CROWN 2033, MOBILE MECHANIC CLOVELLY, CAR MECHANIC 2035, CAR REPAIRS 2035, AUTO REPAIR 2035,
# RESTAURANT 2031, CAFE 2031, COFFEE SHOP 2031, COFFEE SHOP MILSONS POINT

print(a['status'])
print(a['time_log'])

# print("Exposed flask api ... ")

app = Flask(__name__)


# print(" -------------------------- Memery Occupy Log ------------------------------")
# helper.print_memory_occupy(list(locals().items()))


@app.route('/api/search_engine', methods=['GET', 'POST'])
def search_engine():
    logger.debug(f'search_engine: RECEIVED: request url: {request.url}')

    query = request.args.get('query')
    query_lat = request.args.get('lat')
    query_long = request.args.get('long')
    query_topN = request.args.get('topN')
    query_page = request.args.get('page')
    query_radius = request.args.get('radius')

    if query is not None:
        query_lat_lon = []
        if query_lat is not None and query_long is not None:
            try:
                query_lat = float(query_lat)
                query_long = float(query_long)
                query_lat_lon = [(query_lat, query_long)]
            except ValueError:
                query_lat_lon = []

        query_topN = int(query_topN) if query_topN is not None else 1000
        query_page = int(query_page) if query_page is not None else 1
        query_radius = float(query_radius) if query_radius is not None else 40000
        query = query.upper()
        search_result = extract(query, lat_lon=query_lat_lon, param_radius=query_radius, topN=query_topN,
                                page=query_page)

        logger.debug(f'search_engine: SENT: {search_result}, request url: {request.url}')

        return jsonify(search_result)
    else:
        final = str(
            jsonify({'status': 'failed', 'exception': 'please provide query YES', 'result': [], 'time_log': []}))
        logger.debug(f'search_engine: SENT error: {final}, request url: {request.url}')

        return jsonify({'status': 'failed', 'exception': 'please provide query YES', 'result': [], 'time_log': []})


def get_category(query_list):
    if query_list is None or len(query_list) == 0:
        return jsonify({})
    results = {}
    for sub_query in query_list:
        parse = nlp(sub_query.lower())
        sub_query = sub_query.upper()
        if parse.vector_norm == 0:
            results[sub_query] = {"category": "OTHER ITEMS", "shopping_id": "", "score": 1}
        else:
            norm_vector = np.array(parse.vector / parse.vector_norm)
            cos_similarity = np.matmul(g_categories_norm_vector_mat, norm_vector.transpose())
            max_cat_index = np.argmax(cos_similarity)
            max_cat_id = list(g_categories_dict.keys())[max_cat_index]
            most_candidate_cat = g_categories_dict[max_cat_id]
            most_candidate_cat_score = float(cos_similarity[max_cat_index])
            if most_candidate_cat_score < 0.75:
                results[sub_query] = {"category": "OTHER ITEMS", "shopping_id": "", "score": 1}
            else:
                results[sub_query] = {"category": most_candidate_cat, "shopping_id": max_cat_id,
                                      "score": most_candidate_cat_score}

    return results


# /api/shopping_ml?query="2 beef steaks"
# /api/shopping_ml?query=["a kilo of bananas", "beef cutlets", "coffee"]
# return:
#   {"2 beef seaks": "Meat"}
#   {"a kilo of bananas": "Fruit", "beef cutlets": "Meat", "coffee": "OTHER ITEMS"}

@app.route('/api/shopping_ml', methods=['GET', 'POST'])
def shopping_ml():
    logger.debug(f'shopping_ml: RECEIVED: {request.url}')

    if request.method == 'GET':
        request_obj = request.args
    else:
        request_obj = json.loads(request.data)

    query = request_obj.get("query")
    query_array = []
    if query is None or len(query) == 0:
        final = str(jsonify({'status': 'error', 'description': 'Please input a query parameter value'}))
        logger.debug(f'shopping_ml: SENT error: {final}, request url: {request.url}')

        return jsonify({'status': 'error', 'description': 'Please input a query parameter value'})

    try:
        query_array = json.loads(query)
        if not isinstance(query_array, list):
            final = str(jsonify({'status': 'error', 'description': 'Input parameter should be an array in your case.'}))
            logger.debug(f'shopping_ml: SENT error: {final}, request url: {request.url}')

            return jsonify({'status': 'error', 'description': 'Input parameter should be an array in your case.'})
    except Exception as e:
        print(e)
        query_array = [str(query)]

    results = get_category(query_array)
    # {"result": {query:{"category": "OTHER ITEMS", "shopping_id": "", "score": 1}}, "status": "success"})

    final = str(jsonify({"result": results, "status": "success"}))
    logger.debug(f'shopping_ml: SENT: {final}, request url: {request.url}')

    return jsonify({"result": results, "status": "success"})


if __name__ == '__main__':
    app.run(debug=False, host="localhost", port=8101, threaded=True)
    # app.run(debug=False, host="0.0.0.0", port=8000, threaded=True)
    # app.run(debug=False, host="0.0.0.0", port=8000, threaded=True, ssl_context='adhoc')
    # app.run(debug=False, host="0.0.0.0", port=443, threaded=True, ssl_context=('cert3.crt', 'privkey3.pem'))
    # app.run(debug=False, host="0.0.0.0", port=443, threaded=True,
    # ssl_context=('jmkesxt.quikfindsydney.com.au.crt', 'jmkesxt.quikfindsydney.com.au_privkey.pem'))
