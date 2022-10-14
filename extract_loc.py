import json
import pickle

import numpy as np

import helper as helper
import const as const
from itertools import combinations
from time import time

from gensim.models import KeyedVectors
from spellchecker import SpellChecker

print("-----------------------------------------------------------------------------")
print("---------------------------- Extract Loc Test -------------------------------")
print("-----------------------------------------------------------------------------")

# g4 = {
#     0: {11195.0: {'town_dist': -1.3, 'biz': {28437: 0.0, 95352: 0.0, 186332: 0.0, 534300: 0.0, 571925: 0.0}}},
#     1100:
#         {
#             11195.0: {'town_dist': 0.8, 'biz': {1448902: 0.0, 372493: 0.1, 373824: 0.2}},
#             11196.0: {'town_dist': -1.2, 'biz': {1448902: 0.0, 547725: 0.0, 557490: 0.0}},
#             11197.0: {'town_dist': -1.3, 'biz': {1448902: 0.0}}
#         }
# }
# g4 = sorted(g4.items(), key=lambda x: x[0], reverse=True)
# for (premium_level, g5) in g4:
#     g5 = sorted(g5.items(), key=lambda x: x[1]['town_dist'])
#     for (tid, g6) in g5:
#         print('---------g5 -------------')
#         print(g5)
#
#         g6 = sorted(g6.items(), key=lambda x: x[0])
#         print(g6)
#         exit(1)
# exit(1)

# print("Test haversine ...")
# start = (-33.862729, 151.207066)
# end = (-33.8670207, 151.2173064)
# dist = helper.haversine(start, end)
# print(dist)
# exit(1)

# with open('Keywords/organic_premium_keyword_biz.pkl', 'rb') as f:
#     organic_premium_keyword_biz = pickle.load(f)
# with open('Keywords/loc_premium_keyword_biz.pkl', 'rb') as f:
#     loc_premium_keyword_biz = pickle.load(f)
# print(organic_premium_keyword_biz['MECHANIC'])
# exit(1)

# with open('Keywords/loc_keyword_biz.pkl', 'rb') as f:
#     loc_keyword_biz = pickle.load(f)
#
# with open('Keywords/organic_keyword_biz.pkl', 'rb') as f:
#     organic_keyword_biz = pickle.load(f)
# print(loc_keyword_biz[helper.getMatchKeyword(loc_keyword_biz, 'EASTLAKES', 'upper')])
# exit(1)

# with open('Keywords/business_keywords.pkl', 'rb') as f:
#     business_keywords = pickle.load(f)
# print(business_keywords[14])
# exit(1)

print("Loading keywords from pkl and json ... ")

spell_vocab = SpellChecker(local_dictionary='Keywords/spell_keyword_vocab.json')

with open('Keywords/spell_keyword_vocab.json', 'r') as f:
    spell_vocab_dict = json.load(f)
with open('Keywords/organic_keyword_vocab.json', 'r') as f:
    spell_org_dict = json.load(f)
with open('Keywords/loc_keyword_vocab.json', 'r') as f:
    spell_loc_dict = json.load(f)
with open('Keywords/town_keyword_vocab.json', 'r') as f:
    spell_town_dict = json.load(f)

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
                print('town_keyword', keyword, 'match_town_keyword', match_town_keyword)
                if match_town_keyword is not None:
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

        # if town_name_0 is not None:
        #     break
    if town_set is not None and len(town_set) > 0:
        town_name_0 = TOWN_INFO[int(list(town_set)[0])]['name']
        town_id_list = [int(tid) for tid in list(town_set)]
    return town_name_0, town_id_list


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

        word = word.lower()
        pl_word = helper.getPlural(word)
        sl_word = helper.getSingular(word)
        print(word, pl_word, sl_word)
        if spell_vocab.unknown([word]) and pl_word is not None and spell_vocab.unknown([pl_word]) \
                and sl_word is not None and spell_vocab.unknown([sl_word]):
            word = spell_vocab.correction(word)
            print('correction', word)
        match_non_loc_keyword = helper.getMatchKeyword(spell_vocab_dict, word, 'lower')
        if match_non_loc_keyword is not None:
            words = [match_non_loc_keyword]
        else:
            words = []
        print('non_loc_keyword', word, 'match_non_loc_keyword', match_non_loc_keyword)
        for word1 in words:
            if word1 in spell_org_dict:
                # if word not in spell_loc_dict or (word in spell_loc_dict and spell_org_dict[word] >=
                # spell_loc_dict[word]):
                non_loc_query[word1.upper()] = spell_org_dict[word1]
                # if word is also loc, its priority change to lower.
                if word1 in spell_loc_dict:
                    print('score1', non_loc_query[word1.upper()])
                    print('score2', spell_loc_dict[word1])
                    non_loc_query[word1.upper()] -= (spell_loc_dict[word1] * 10)
            if word1.upper() in const.populate_search_words:
                pop_words.append(word1.upper())

            match_loc_keyword = helper.getMatchKeyword(spell_loc_dict, word1, 'lower')

            print('loc_keyword', word, 'match_loc_keyword', match_loc_keyword)
            if match_loc_keyword is not None:
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
                    # match_loc_prob_keyword = helper.getMatchKeyword(loc_keyword_prob, match_loc_keyword, 'upper')
                    # print('loc_prob_keyword', match_loc_keyword, 'match_loc_prob_keyword', match_loc_prob_keyword)
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

                    print("prob end")
                    loc_query[word1.upper()] = (pose, spell_loc_dict[word1])
                    last_loc_word = word1.upper()

    print('non_loc_query before sort', non_loc_query)
    _non_loc_query = sorted(non_loc_query.items(), key=lambda x: x[1], reverse=True)
    print('_non_loc_query', _non_loc_query)

    _loc_query = sorted(loc_query.items(), key=lambda x: x[1])
    _loc_query = {item[0]: item[1][0] for item in _loc_query}
    print('_loc_query', _loc_query)
    # if only non_loc is enough for topN, remove both keywords.
    non_loc_query = []
    for word, score in _non_loc_query:
        non_loc_query.append(word)
        # only non-loc keywords is all appended.
        # if meaningful non-loc+loc also is appended.
        # Felix: Only if non_loc_keyword is in loc_query
        if len(non_loc_query) > 1 and word.upper() in _loc_query and spell_org_dict[word.lower()] < topN \
                and word.lower() in spell_loc_dict:
            # reach predicted
            print('pop', word, spell_org_dict[word.lower()])
            non_loc_query = non_loc_query[:-1]
            break
    loc_query = {k: v for k, v in _loc_query.items() if k not in non_loc_query}

    print('loc_query', loc_query)
    # if input is one, consider only as non-location
    if len(text) == 1 and len(loc_query) == 1 and len(non_loc_query) == 1:
        loc_query = {}

    # In loc keywords, town keywords change to 6 (town pose)
    if town_name_list is not None:
        town_name_keywords = town_name_list.split()
        loc_query = {k: 6 if k in town_name_keywords else pose for k, pose in loc_query.items()}
        print('town_name_list', loc_query)

    # empty non-loc is the same as in populated keywords
    if len(non_loc_query) == 0 and len(pop_words) > 0:
        non_loc_query = pop_words

    return non_loc_query, loc_query


def extract(query, lat_lon=None, param_radius=40000, topN=1000, page=1, showPrint=False):
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
        # print(query_in_w2v)
        query_not_in_w2v = [w for w in query if w.lower() not in w2v]
        # print(query_not_in_w2v)

        # query_in_w2v = [w for w in query_in_w2v
        #                if max(w2v.cosine_similarities(w2v[w.lower()], ignored_keywords_vec)) < 0.7]

        query_extracted = query_in_w2v + query_not_in_w2v
        print('query_extracted', query_extracted)

        query_preproc = [const.loc_keyword_pose[keyword] if keyword in const.loc_keyword_pose else keyword for keyword
                         in query_extracted]
        print('query_preproc', query_preproc)
        loc_town_name, loc_town_id_list = extract_town(query_preproc)

        print(' ------ extract_town result ------ ')
        print('loc_town_name', loc_town_name)
        print('loc_town_id_list', loc_town_id_list)

        non_loc_query, loc_query = extract_loc(query_preproc, loc_town_name, topN)

        print(' ------ extract_loc result ------ ')
        print('non_loc_query', non_loc_query)
        print('loc_query', loc_query)

        # If non-loc is empty, try to use ignored keywords.
        # DR = DOCTOR
        if len(non_loc_query) == 0:
            if 'DR' in query_extracted:
                non_loc_query.append('DOCTOR')

        # if input is directly town, start_town is just it.
        best_matched_town_lat_lon, best_matched_town_id = None, 0
        if len(lat_lon) > 0 and lat_lon[0] != (None, None) and loc_town_name is not None:

            distance = param_radius
            for tid in loc_town_id_list:
                temp_dist = helper.haversine(lat_lon[0], TOWN_INFO[tid]['lat_lon']) - TOWN_INFO[tid]['radius']
                if temp_dist < distance:
                    best_matched_town_id = tid
                    best_matched_town_lat_lon = TOWN_INFO[tid]['lat_lon']
                    print('best_matched_town', tid, TOWN_INFO[tid]['name'])
                    if temp_dist < 0:
                        break
                    distance = temp_dist

        # loc_query:  {keyword: pose}

        # not exist town keyword

        if const.pose_keywords['TOWN'] not in loc_query.values() and len(lat_lon) != 0:
            print('pose_keywords', const.pose_keywords['TOWN'])
            if best_matched_town_lat_lon is not None:
                tid = best_matched_town_id
            else:
                tid = loc_nearest_match(lat_lon[0])

            print('nearest town', TOWN_INFO[tid]["name"])

            # loc_query_town = {
            #     word if word.lower() in spell_loc_dict else spell_vocab.correction(word).upper():
            #         const.pose_keywords['TOWN'] for word in (TOWN_INFO[tid]["name"].split())
            # }

            loc_query_town = {
                helper.getMatchKeyword(spell_loc_dict, word, 'upper')
                if helper.getMatchKeyword(spell_loc_dict, word, 'upper') is not None
                else spell_vocab.correction(word).upper():
                    const.pose_keywords['TOWN'] for word in (TOWN_INFO[tid]["name"].split())
            }

            # if TOWN_INFO[tid]["state_code"] is not None and len(TOWN_INFO[tid]["state_code"]) > 0:
            #     loc_query_town.update({
            #         word if word.lower() in spell_loc_dict else spell_vocab.correction(word).upper():
            #             const.pose_keywords['STATE'] for word in (TOWN_INFO[tid]["state_code"].split())
            #     })

            if TOWN_INFO[tid]["state_code"] is not None and len(TOWN_INFO[tid]["state_code"]) > 0:
                loc_query_town.update({
                    helper.getMatchKeyword(spell_loc_dict, word, 'upper')
                    if helper.getMatchKeyword(spell_loc_dict, word, 'upper') is not None
                    else spell_vocab.correction(word).upper():
                        const.pose_keywords['STATE'] for word in (TOWN_INFO[tid]["state_code"].split())
                })
            print('loc_query_town', loc_query_town)
            # user lat_lon town is the lowest priority
            loc_query_town.update(loc_query)
            loc_query = loc_query_town
        print(' ------- Last Result ------ ')
        print('non_loc_query', non_loc_query)
        print('loc_query', loc_query)
    except Exception as e:
        print(e)
        exit(1)


# a = extract('PLUMBER 2032', [(-33.8670207, 151.2173064)])
# a = extract('GAS FITTER 2035', [(-33.8670207, 151.2173064)])
# a = extract('MOBILE MECHANIC CLOVELLY', [(-33.8670207, 151.2173064)])
# a = extract('jb hi fi', [(-33.8670207, 151.2173064)])
# a = extract('HOT WATER PLUMBER 2032', [(-33.8670207, 151.2173064)])
# a = extract('RESTAURANT MCMAHONS POINT', [(-33.8670207, 151.2173064)])
# a = extract('FOOD TAKEOUTS WYNYARD', [(-33.920, 151.243)], 20, 1000, 1, True)
a = extract('PLUMBERS EASTLAKES', [(-33.868112, 151.22349)], 40, 1000, 1, True)

# TOOTH FILLING DACEYVILLE, CHIPPED TOOTH DACEYVILLE, TOOTH FILLING KINGSFORD, CHIPPED TOOTH KINGSFORD,
# DENTAL CROWN 2033, MOBILE MECHANIC CLOVELLY, CAR MECHANIC 2035, CAR REPAIRS 2035, AUTO REPAIR 2035,
# RESTAURANT 2031, CAFE 2031, COFFEE SHOP 2031, COFFEE SHOP MILSONS POINT
print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
