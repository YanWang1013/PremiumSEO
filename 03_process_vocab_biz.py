"""
Created by: DSA LinGene - Eugene
Email: dsa.lingene@outlook.com
"""

import pickle
import json
from difflib import SequenceMatcher
import const as const
import helper as helper

# Dump PKL & JSON
# 1. Keywords/organic_temp_keyword_vocab.json
# 2. Keywords/organic_temp_keyword_biz.pkl
# 3. Keywords/organic_keyword_vocab.json
# 4. Keywords/organic_keyword_merged.txt
# 5. Keywords/organic_keyword_biz.pkl

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 03 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading town data from au_towns")

au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))

TOWN_NAME = {town_name: '' for town_name in au_towns['name'] if town_name not in const.except_town_list}
TOWN_NAME.update({urban_area: '' for urban_area in au_towns['urban_area'] if urban_area is not None})
TOWN_NAME.update({state_code: '' for state_code in au_towns['state_code'] if state_code is not None})
TOWN_NAME_copy = TOWN_NAME.copy()
# 'COLES': '', 'COLE': ''
TOWN_NAME.update({town_name + 'S': '' for town_name in TOWN_NAME_copy})

del au_towns
del TOWN_NAME_copy

print("Loading organic keywords from META_DATA_INDEX")

META_DATA_INDEX = pickle.load(open('Database/META_DATA_INDEX.pkl', 'rb'))

for col in ['B', 'A', 'P1', 'P2', 'G1', 'G1T', 'G2', 'G2D', 'G3K', 'G4P', 'G5H', 'T1', 'T2', 'T3', 'S1', 'S2']:
    if col not in ['S1', 'S2']:
        META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list(x, col))
    elif col == 'S2':
        META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list_S2(x, col))
    else:
        META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list_S(x, col))

result = META_DATA_INDEX.B + META_DATA_INDEX.P1 + META_DATA_INDEX.P2 + META_DATA_INDEX.G1 + \
         META_DATA_INDEX.G1T + META_DATA_INDEX.G2 + META_DATA_INDEX.G2D + META_DATA_INDEX.G3K + META_DATA_INDEX.G4P + \
         META_DATA_INDEX.G5H + META_DATA_INDEX.T1 + META_DATA_INDEX.T2 + META_DATA_INDEX.T3 + META_DATA_INDEX.S1 + \
         META_DATA_INDEX.S2
organic_keywords = {}
try:
    organic_keywords = {idx: words if len(words) != 0 else [None] for idx, words in zip(META_DATA_INDEX.id, result)}
    organic_keywords = {k: [vi for i, vi in enumerate(v)
                            if vi is not None and (i == 0 or i > 0 and vi not in TOWN_NAME)]
                        for k, v in organic_keywords.items()}
except Exception as e:
    print(e)

del META_DATA_INDEX
del TOWN_NAME
del result
print("Checking for digit and stopwords and Dumping for temp pkl and json")

temp_organic_keyword_biz = {}
temp_keywords_vocab = {}

for b, v in organic_keywords.items():
    try:
        vii = []
        for vi in v:
            if vi[0] in const.digits or vi[0] == 'u':
                continue
            vi = ''.join([' ' if c in const.digits else c for c in vi])
            vii += vi.split()

        for word in set(vii):
            if len(word) < 2 or word in const.stopwords:
                continue
            if word in temp_organic_keyword_biz:
                # if b not in temp_organic_keyword_biz[word]:
                temp_organic_keyword_biz[word][b] = ''
                temp_keywords_vocab[word] += 1
            else:
                temp_organic_keyword_biz[word] = {b: ''}
                temp_keywords_vocab[word] = 1
    except Exception as e:
        print(e)

del organic_keywords

temp_keywords_vocab = sorted(temp_keywords_vocab.items(), key=lambda x: x[0])
with open('Keywords/organic_temp_keyword_vocab.json', 'w') as f:
    json.dump(temp_keywords_vocab, f)

with open('Keywords/organic_temp_keyword_biz.pkl', 'wb') as f:
    pickle.dump(temp_organic_keyword_biz, f)

print("Making weight for keywords")

temp4w_counting = {}

organic_keyword_biz = {}
keywords_vocab = {}
# merged_keywords = []

for word, count in temp_keywords_vocab:

    candidates = {}
    for vocab_w in list(keywords_vocab)[-40:]:
        score = SequenceMatcher(None, vocab_w, word).ratio()
        if score > const.SequenceMatcher_LowerLimit:
            candidates[vocab_w] = score

    if len(candidates) == 0:
        organic_keyword_biz[word] = temp_organic_keyword_biz[word]
        keywords_vocab[word] = count
        temp4w_counting[word] = count
    else:
        replaced = sorted(candidates, key=lambda x: x[1], reverse=True)[0]
        if keywords_vocab[replaced] < count:
            organic_keyword_biz[word] = temp_organic_keyword_biz[word]

            # organic_keyword_biz[word] += organic_keyword_biz[replaced]
            for r in organic_keyword_biz[replaced]:
                if r not in organic_keyword_biz[word]:
                    organic_keyword_biz[word][r] = ''

            keywords_vocab[word] = count
            temp4w_counting[word] = count + keywords_vocab[replaced]
            organic_keyword_biz.pop(replaced, None)
            keywords_vocab.pop(replaced, None)
        else:
            # organic_keyword_biz[replaced] += temp_organic_keyword_biz[word]
            for t in temp_organic_keyword_biz[word]:
                if t not in organic_keyword_biz[replaced]:
                    organic_keyword_biz[replaced][t] = ''

            temp4w_counting[replaced] += count

        # merged_keywords.append(word + " " + replaced)

del temp_keywords_vocab
del temp_organic_keyword_biz

print("Checking for plural")
# remove -s, -ies
temp = keywords_vocab.copy()
# spell_keyword = SpellChecker(local_dictionary='Keywords/spell_keyword_vocab.json')

for word in temp:
    # Felix: if word is 'leaks', return 'leake' from spell_vocab.correction.
    # if 'leaks' is unknown word, put 'leake' instead of 'leaks'
    # if spell_keyword.unknown([word.lower()]):
    #     word = spell_keyword.correction(word.lower()).upper()

    match_word = None
    # if word[-1] == 'S' and word[:-1] in keywords_vocab and word not in const.except_plural_list:
    #     match_word = word[:-1]
    #     # if word == 'LEAKS':
    #     # print(word + ' - ' + match_word)
    #
    # elif word[-3:] == 'IES' and (word[:-3] + 'Y') in keywords_vocab:
    #     match_word = word[:-3] + 'Y'
    #     # print(word + ' - ' + match_word)
    if word not in const.except_plural_list:
        sl_word = helper.getSingular(word.lower())
        if sl_word is not None and sl_word.upper() in keywords_vocab:
            match_word = sl_word.upper()

    if match_word is not None and word != match_word and match_word in keywords_vocab and word in keywords_vocab:
        if temp4w_counting[word] > temp4w_counting[match_word]:
            temp4w_counting[word] += temp4w_counting[match_word]
            keywords_vocab[word] += keywords_vocab[match_word]
            organic_keyword_biz[word].update(organic_keyword_biz[match_word])
            keywords_vocab.pop(match_word, None)
            organic_keyword_biz.pop(match_word, None)
        else:
            temp4w_counting[match_word] += temp4w_counting[word]
            keywords_vocab[match_word] += keywords_vocab[word]
            organic_keyword_biz[match_word].update(organic_keyword_biz[word])
            keywords_vocab.pop(word, None)
            organic_keyword_biz.pop(word, None)
        print(word, temp4w_counting[word], match_word, temp4w_counting[match_word])

keywords_vocab = {word.lower(): temp4w_counting[word] for word in sorted(keywords_vocab) if temp4w_counting[word] > 2}
with open('Keywords/organic_keyword_vocab.json', 'w') as f:
    json.dump(keywords_vocab, f)

# Felix: Never used Keywords/organic_keyword_merged.txt

# with open('Keywords/organic_keyword_merged.txt', 'w') as f:
#     for item in merged_keywords:
#         f.write("%s\n" % item)

'''
final_organic_keyword_biz = {}
for k, v in organic_keyword_biz.items():
    vv = set(v)
    final_organic_keyword_biz[k] = [item for item in vv]
'''
with open('Keywords/organic_keyword_biz.pkl', 'wb') as f:
    pickle.dump(organic_keyword_biz, f)

# print(organic_keyword_biz['FITTER'])
# pickle.dump(organic_keyword_biz, open('Keywords/organic_keyword_biz.pkl', 'wb'))

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))

'''
bt = 0
for item in chunks(organic_keywords, 100000):
    bt+=1
    print("Chunk Start", bt)
    pickle.dump(item, open('Keywords/organic_Keywords_spacy/{}.pkl'.format(bt), 'wb'))
    print("Chunk End", bt)
'''
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 03 ------------------------------")
print("-----------------------------------------------------------------------------")
