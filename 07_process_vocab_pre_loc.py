"""
Created by: DSA LinGene - Eugene
Email: dsa.lingene@outlook.com
"""

import pickle
import json
import helper as helper
from spellchecker import SpellChecker

# Dump PKL & JSON
# 1. Keywords/loc_premium_temp_keyword_vocab.json
# 2. Keywords/loc_premium_keyword_vocab.json
# 3. Keywords/loc_premium_keyword_biz.pkl

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 07 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading T3 data from META_DATA_INDEX")

spell_keyword = SpellChecker(local_dictionary='Keywords/spell_keyword_vocab.json')

META_DATA_INDEX = pickle.load(open('Database/META_DATA_INDEX.pkl', 'rb'))

for col in ['S2', 'PREMIUM']:
    if col == 'PREMIUM':
        META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list(x, col))
    else:
        META_DATA_INDEX[col] = META_DATA_INDEX[col].apply(lambda x: helper.json_to_list_S2(x, col))

result = META_DATA_INDEX.S2
premium_value = META_DATA_INDEX.PREMIUM
loc_keywords = {b: [words, premium_value] for b, words, premium_value in zip(META_DATA_INDEX.id, result, premium_value)
                if len(words) > 0}

del META_DATA_INDEX
del result
del premium_value

# 1448851: [[None], [None]]
# 1448901: [[['DACEYVILLE', '2032'], ['CLOVELLY', '2031'], ['KINGSFORD', '2032'],
# ['PAGEWOOD', '2035'], ['MAROUBRA', '2035'], ['COOGEE', '2034'], ['RANDWICK', '2031'], ['KENSINGTON', '2033'],
# ['SOUTH COOGEE', '2034']], [None]]

# {"S1": ["RANDWICK"]}
# {"T1": "DENTIST"}
# {"T2": ["DENTIST", "DENTISTRY", "DENTAL IMPLANTS", "DENTAL CROWN", "DENTAL CLINIC", "ORTHODONTIST", "TOOTH FILLING",
# "CHIPPED TOOTH", "ORTHODONTICS", "INVISALIGN", "VENEERS"]}
# {"S2": [["DACEYVILLE", "2032"], ["CLOVELLY", "2031"], ["KINGSFORD", "2032"], ["PAGEWOOD", "2035"],
# ["MAROUBRA", "2035"], ["COOGEE", "2034"], ["RANDWICK", "2031"], ["KENSINGTON", "2033"], ["SOUTH COOGEE", "2034"]]}
# {"T3": ["DENTIST", "DENTISTRY", "DENTAL IMPLANTS", "DENTAL CROWN", "DENTAL CLINIC", "ORTHODONTIST", "TOOTH FILLING",
# "CHIPPED TOOTH", "ORTHODONTICS", "INVISALIGN", "VENEERS"]}
try:
    loc_keywords = {b: [[vii for vi in v[0] if vi is not None for vii in vi.split() if len(vii) > 0], v[1]] for b, v in
                    loc_keywords.items()}
except AttributeError:
    print("--- vi split error ---")
except Exception as e:
    print(e)

print("Checking for spelling correction and Dumping to location premium keyword")

loc_keyword_biz = {}
temp_keywords_vocab = {}

for b, v in loc_keywords.items():
    for word in v[0]:
        # Felix: if word is 'leaks', return 'leake' from spell_vocab.correction.
        # if 'leaks' is unknown word, put 'leake' instead of 'leaks'
        # For premium keywords, don't spell check, since those are already human verified.
        # if spell_keyword.unknown([word.lower()]):
        #     spelled = spell_keyword.correction(word.lower()).upper()
        #     # print(word + ' : ' + spelled)
        # else:
        #     spelled = word
        spelled = word
        if spelled in loc_keyword_biz:
            loc_keyword_biz[spelled][b] = v[1]
            temp_keywords_vocab[spelled] += 1
        else:
            loc_keyword_biz[spelled] = {}
            loc_keyword_biz[spelled][b] = v[1]
            temp_keywords_vocab[spelled] = 1

temp_keywords_vocab = sorted(temp_keywords_vocab.items(), key=lambda x: x[0])
with open('Keywords/loc_premium_temp_keyword_vocab.json', 'w') as f:
    json.dump(temp_keywords_vocab, f)

with open('Keywords/loc_premium_keyword_biz.pkl', 'wb') as f:
    pickle.dump(loc_keyword_biz, f)

keywords_vocab = {word.lower(): count for (word, count) in temp_keywords_vocab}
with open('Keywords/loc_premium_keyword_vocab.json', 'w') as f:
    json.dump(keywords_vocab, f)

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 07 ------------------------------")
print("-----------------------------------------------------------------------------")
