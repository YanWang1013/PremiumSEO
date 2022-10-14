"""
Created by: DSA LinGene - Eugene
Email: dsa.lingene@outlook.com
"""

import pickle
import json
import helper as helper
import const as const

# Dump PKL & JSON
# 1. Keywords/loc_temp_keyword_vocab.json
# 2. Keywords/loc_keyword_vocab.json
# 3. Keywords/loc_keyword_biz.pkl
# 4. Keywords/loc_keyword_prob.json

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 04 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading town data from au_towns")

au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))

TOWN_KEYS = {}
TOWN_INFO = {'name': {}, 'urban_area': {}, 'state_code': {}, 'state': {}, 'postcode': {}}
for idx, town in au_towns.iterrows():

    town_id = town['id']
    items = ['name', 'urban_area', 'state_code', 'state', 'postcode']
    TOWN_KEYS[town_id] = {}
    TOWN_KEYS[town_id]['name'] = town['name'].upper() if town['name'] is not None and len(town['name']) > 1 else ''
    TOWN_KEYS[town_id]['urban_area'] = town['urban_area'].upper() if town['urban_area'] is not None and len(
        town['urban_area']) > 1 else ''
    TOWN_KEYS[town_id]['state_code'] = town['state_code'].upper() if town['state_code'] is not None and len(
        town['state_code']) > 1 else ''
    TOWN_KEYS[town_id]['state'] = town['state'].upper() if town['state'] is not None and len(town['state']) > 1 else ''
    TOWN_KEYS[town_id]['postcode'] = town['postcode'].upper() if town['postcode'] is not None and len(
        town['postcode']) > 1 else ''

    TOWN_INFO['name'][TOWN_KEYS[town_id]['name']] = ''
    TOWN_INFO['urban_area'][TOWN_KEYS[town_id]['urban_area']] = ''
    TOWN_INFO['state_code'][TOWN_KEYS[town_id]['state_code']] = ''
    TOWN_INFO['state'][TOWN_KEYS[town_id]['state']] = ''
    TOWN_INFO['postcode'][TOWN_KEYS[town_id]['postcode']] = ''

del au_towns

print("Loading keyword data from META_DATA_INDEX")

META_DATA_INDEX = pickle.load(open('Database/META_DATA_INDEX.pkl', 'rb'))

META_DATA_INDEX['S2'] = META_DATA_INDEX['S2'].apply(lambda x: helper.json_to_list_S(x, 'S2'))

# result = META_DATA_INDEX.A + META_DATA_INDEX.S1 + META_DATA_INDEX.S2

loc_keyword_biz = {}
temp_keywords_vocab = {}
loc_keyword_prob = {}


def get_prob(b, key, words):
    probability = None
    mul_factor = 10 ** (key - 6)
    for vi in words:
        if vi is None or len(vi) == 0 or vi[0] == 'u':
            continue
        try:
            vii = [v for v in vi.split() if v not in const.stopwords]
            if len(vii) > 0:
                probability = 1 / len(vii)

            for word in vii:
                if word in loc_keyword_biz:
                    if b > 0:
                        if b not in loc_keyword_biz[word]:
                            loc_keyword_biz[word][b] = [0, 0, 0, 0, 0, 0, 0]
                            loc_keyword_biz[word][b][key] = probability * mul_factor
                        else:
                            loc_keyword_biz[word][b][key] = max(probability * mul_factor, loc_keyword_biz[word][b][key])

                    temp_keywords_vocab[word] += 1

                    if loc_keyword_prob[word][key] < probability:
                        loc_keyword_prob[word][key] = probability
                else:
                    loc_keyword_biz[word] = {}
                    if b > 0:
                        loc_keyword_biz[word][b] = [0, 0, 0, 0, 0, 0, 0]
                        loc_keyword_biz[word][b][key] = probability * mul_factor

                    temp_keywords_vocab[word] = 1

                    loc_keyword_prob[word] = [0, 0, 0, 0, 0, 0, 0]
                    loc_keyword_prob[word][key] = probability
        except AttributeError:
            print("--- vi error ---")
            print(vi)


print("Making probability weight for location keywords and Dumping to location keyword and vocabulary")
idx = 0
for b, town_id, s2, road, house_number, h in zip(META_DATA_INDEX.id, META_DATA_INDEX.town_id, META_DATA_INDEX.S2,
                                                 META_DATA_INDEX.A_ROAD, META_DATA_INDEX.A_HOUSE_NUMBER,
                                                 META_DATA_INDEX.A_HOUSE):
    idx += 1
    if town_id == 0 or town_id not in TOWN_KEYS:
        continue

    # 6: town,  5: urban_area, 4: st,  3: house_n,  2: house,  1: post,  0: other
    get_prob(b, 6, [TOWN_KEYS[town_id]['name']])
    get_prob(b, 5, [TOWN_KEYS[town_id]['urban_area']])
    get_prob(b, 4, [road])
    get_prob(b, 3, [house_number])
    get_prob(b, 2, [h])
    get_prob(b, 1, [TOWN_KEYS[town_id]['postcode']])
    get_prob(b, 0, [TOWN_KEYS[town_id]['state'], TOWN_KEYS[town_id]['state_code']])

    # s2 separating and consider
    # loc format: ['DACEYVILLE', '2032']
    if s2 is not None:
        for loc in s2:
            if loc is not None:
                if loc[0] in TOWN_INFO['name']:
                    get_prob(b, 6, [loc[0]])
                elif loc[0] in TOWN_INFO['urban_area']:
                    get_prob(b, 5, [loc[0]])
                elif loc[1] in TOWN_INFO['postcode']:
                    get_prob(b, 1, [loc[1]])
                else:
                    get_prob(b, 0, [loc])  # Not sure

# consider au_towns (maybe not exist in META_DATA)
for town_id in TOWN_KEYS:
    # 6: town,  5: urban_area, 4: st,  3: house_n,  2: house,  1: post,  0: other
    get_prob(0, 6, [TOWN_KEYS[town_id]['name']])
    get_prob(0, 5, [TOWN_KEYS[town_id]['urban_area']])
    get_prob(0, 1, [TOWN_KEYS[town_id]['postcode']])
    get_prob(0, 0, [TOWN_KEYS[town_id]['state'], TOWN_KEYS[town_id]['state_code']])

del META_DATA_INDEX
del TOWN_INFO
del TOWN_KEYS

temp_keywords_vocab = sorted(temp_keywords_vocab.items(), key=lambda x: x[0])
with open('Keywords/loc_temp_keyword_vocab.json', 'w') as f:
    json.dump(temp_keywords_vocab, f)

keywords_vocab = {word.lower(): count for (word, count) in temp_keywords_vocab}

with open('Keywords/loc_keyword_vocab.json', 'w') as f:
    json.dump(keywords_vocab, f)

pickle.dump(loc_keyword_biz, open('Keywords/loc_keyword_biz.pkl', 'wb'))

with open('Keywords/loc_keyword_prob.json', 'w') as f:
    json.dump(loc_keyword_prob, f)

'''
bt = 0
for item in chunks(final_loc_keyword_biz, 5000):
    bt+=1
    print("Chunk Start", bt)
    pickle.dump(item, open('Keywords/loc_keyword_biz/loc_keyword_biz_{}.pkl'.format(bt), 'wb'))
    print("Chunk End", bt)
'''

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 04 ------------------------------")
print("-----------------------------------------------------------------------------")
