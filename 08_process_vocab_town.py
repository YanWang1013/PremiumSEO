import pickle
import json
from time import time
from spellchecker import SpellChecker
import helper as helper

# Dump PKL & JSON
# 1. Keywords/town_keyword_vocab.json
# 2. Keywords/slow_town_keys.json

print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 08 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading town data from au_towns")

spell_vocab = SpellChecker(local_dictionary='Keywords/spell_keyword_vocab.json')
with open('Keywords/spell_keyword_vocab.json', 'r') as f:
    spell_dict = json.load(f)

au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))

print("Checking for spelling correction and Dumping to town keyword")

town_vocab = {}
slow_keys = {}
inx = 0
for town_id, town_name in zip(au_towns['id'], au_towns['name']):
    inx += 1

    words = town_name.split()
    for word in words:
        old_word = word.lower()
        if len(word) == 0:
            continue
        if word.lower() not in spell_dict:
            start_time = time()
            word = spell_vocab.correction(word.lower()).upper()
            delta = time() - start_time
            if delta > 1:
                slow_keys[word] = delta

        if word in town_vocab:
            town_vocab[word][town_id] = ''
            # if old_word != word.lower():
            #     print(old_word, word.lower())
        else:
            town_vocab[word] = {town_id: ''}
del au_towns
del spell_dict

with open('Keywords/town_keyword_vocab.json', 'w') as f:
    json.dump(town_vocab, f)
del town_vocab
# Felix: Never used Keywords/slow_town_keys.json
# with open('Keywords/slow_town_keys.json', 'w') as f:
#     json.dump(slow_keys, f)

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 08 ------------------------------")
print("-----------------------------------------------------------------------------")
