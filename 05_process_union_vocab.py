import json
import pickle
import const as const
import helper as helper

# Dump PKL & JSON
# 1. Keywords/loc_keyword_vocab.json
# 2. Keywords/loc_keyword_biz.pkl
# 3. Keywords/organic_keyword_vocab.json
# 4. Keywords/organic_keyword_biz.pkl
# 5. Keywords/spell_keyword_vocab.json
print("-----------------------------------------------------------------------------")
print("---------------------------- Start Processing 05 ----------------------------")
print("-----------------------------------------------------------------------------")

print("Loading town data from au_towns and vocabulary data")
au_towns = pickle.load(open('Database/au_towns.pkl', 'rb'))

TOWN_KEYS = {town_keyword.lower(): '' for town_name in au_towns['name'] for town_keyword in town_name.split() if
             town_keyword is not None and len(town_keyword) > 1}
del au_towns

# except_list = {'coles': ''}

with open('Keywords/organic_keyword_vocab.json', 'r') as f:
    org_vocab = json.load(f)
with open('Keywords/loc_keyword_vocab.json', 'r') as f:
    loc_vocab = json.load(f)

with open('Keywords/organic_keyword_biz.pkl', 'rb') as f:
    org_keyword_biz = pickle.load(f)
with open('Keywords/loc_keyword_biz.pkl', 'rb') as f:
    loc_keyword_biz = pickle.load(f)

temp_org_vocab = org_vocab.copy()
temp_loc_vocab = loc_vocab.copy()
temp_org_biz = org_keyword_biz.copy()
temp_loc_biz = loc_keyword_biz.copy()

print("Running remove its plural and merge for Location Keywords")

# for word, count in loc_vocab.items():
#     if word[0] not in const.digits and len(word) > 3 and word[-1] == 's' and word[-2] != 's' and \
#             (word[:-1] in loc_vocab) and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
#         temp_loc_vocab[word[:-1]] += loc_vocab[word]
#         temp_loc_vocab.pop(word)
#         temp_loc_biz[word[:-1].upper()].update(loc_keyword_biz[word.upper()])
#         temp_loc_biz.pop(word.upper())
#     elif word[0] not in const.digits and len(word) > 3 and word[-1] == 's' and word[-2] != 's' and \
#             (word[:-1] in loc_vocab) and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
#         temp_loc_vocab[word[:-1]] = loc_vocab[word]
#         temp_loc_vocab.pop(word, None)
#         temp_loc_biz[word[:-1].upper()] = loc_keyword_biz[word.upper()].copy()
#         temp_loc_biz.pop(word.upper())

for word, count in loc_vocab.items():
    if word[0] not in const.digits and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
        sl_word = helper.getSingular(word)
        pl_word = helper.getPlural(word)
        if sl_word is not None and word != sl_word and sl_word in loc_vocab:
            if sl_word in temp_loc_vocab:
                temp_loc_vocab[sl_word] += loc_vocab[word]
            if word in temp_loc_vocab:
                temp_loc_vocab.pop(word)
            if sl_word.upper() in temp_loc_biz:
                temp_loc_biz[sl_word.upper()].update(loc_keyword_biz[word.upper()])
            else:
                temp_loc_biz[sl_word.upper()] = loc_keyword_biz[word.upper()].copy()
            if word.upper() in temp_loc_biz:
                temp_loc_biz.pop(word.upper())
            print(sl_word, word)
        elif pl_word is not None and word != pl_word and pl_word in loc_vocab:
            temp_loc_vocab[word] += loc_vocab[pl_word]
            if pl_word in temp_loc_vocab:
                temp_loc_vocab.pop(pl_word)
            if word.upper() in temp_loc_biz:
                temp_loc_biz[word.upper()].update(loc_keyword_biz[pl_word.upper()])
            else:
                temp_loc_biz[word.upper()] = loc_keyword_biz[pl_word.upper()].copy()
            if pl_word.upper() in temp_loc_biz:
                temp_loc_biz.pop(pl_word.upper())
            print(pl_word, word)
# loc_vocab = temp_loc_vocab.copy()
#
# for word, count in loc_vocab.items():
#     if word[0] not in const.digits and len(word) > 3 and word[-3:] == 'ies' and (word[:-3] + 'y' in loc_vocab)\
#             and word.upper() not in const.except_plural_list:
#         temp_loc_vocab[word[:-3] + 'y'] += loc_vocab[word]
#         temp_loc_vocab.pop(word)
#         temp_loc_biz[(word[:-3] + 'y').upper()].update(loc_keyword_biz[word.upper()])
#         temp_loc_biz.pop(word.upper())
#     elif word[0] not in const.digits and len(word) > 3 and word[-3:] == 'ies' and (word[:-3] + 'y' in loc_vocab)\
#             and word.upper() not in const.except_plural_list:
#         temp_loc_vocab[word[:-3] + 'y'] = loc_vocab[word]
#         temp_loc_vocab.pop(word)
#         temp_loc_biz[(word[:-3] + 'y').upper()] = loc_keyword_biz[word.upper()].copy()
#         temp_loc_biz.pop(word.upper())

loc_vocab = {word: count for (word, count) in sorted(temp_loc_vocab.items(), key=lambda x: x[0])}

print("Running remove its plural and merge for Organic Keywords")

# print(org_vocab['fitter'])
# for word, count in org_vocab.items():
#     if word[0] not in const.digits and len(word) > 3 and word[-1] == 's' and word[-2] != 's' and \
#             (word[:-1] in org_vocab) and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
#         temp_org_vocab[word[:-1]] += org_vocab[word]
#         temp_org_vocab.pop(word)
#         temp_org_biz[word[:-1].upper()].update(org_keyword_biz[word.upper()])
#         temp_org_biz.pop(word.upper())
#     elif word[0] not in const.digits and len(word) > 3 and word[-1] == 's' and word[-2] != 's' and \
#             (word[:-1] in org_vocab) and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
#         temp_org_vocab[word[:-1]] = org_vocab[word]
#         temp_org_vocab.pop(word)
#         temp_org_biz[word[:-1].upper()] = org_keyword_biz[word.upper()].copy()
#         temp_org_biz.pop(word.upper())

for word, count in org_vocab.items():
    if word[0] not in const.digits and word not in TOWN_KEYS and word.upper() not in const.except_plural_list:
        sl_word = helper.getSingular(word)
        pl_word = helper.getPlural(word)
        if sl_word is not None and word != sl_word and sl_word in org_vocab:
            if sl_word in temp_org_vocab:
                temp_org_vocab[sl_word] += org_vocab[word]
            if word in temp_org_vocab:
                temp_org_vocab.pop(word)
            if sl_word.upper() in temp_org_biz:
                temp_org_biz[sl_word.upper()].update(org_keyword_biz[word.upper()])
            else:
                temp_org_biz[sl_word.upper()] = org_keyword_biz[word.upper()].copy()
            if word.upper() in temp_org_biz:
                temp_org_biz.pop(word.upper())
            print(sl_word, word)
        elif pl_word is not None and word != pl_word and pl_word in org_vocab:
            temp_org_vocab[word] += org_vocab[pl_word]
            if pl_word in temp_org_vocab:
                temp_org_vocab.pop(pl_word)
            if word.upper() in temp_org_biz:
                temp_org_biz[word.upper()].update(org_keyword_biz[pl_word.upper()])
            else:
                temp_org_biz[word.upper()] = org_keyword_biz[pl_word.upper()].copy()
            if pl_word.upper() in temp_org_biz:
                temp_org_biz.pop(pl_word.upper())
            print(pl_word, word)

del TOWN_KEYS
# org_vocab = temp_org_vocab.copy()
#
# for word, count in org_vocab.items():
#     if word[0] not in const.digits and len(word) > 3 and word[-3:] == 'ies' and (word[:-3] + 'y' in org_vocab)\
#             and word.upper() not in const.except_plural_list:
#         temp_org_vocab[word[:-3] + 'y'] += org_vocab[word]
#         temp_org_vocab.pop(word)
#         temp_org_biz[(word[:-3] + 'y').upper()].update(org_keyword_biz[word.upper()])
#         temp_org_biz.pop(word.upper())
#     elif word[0] not in const.digits and len(word) > 3 and word[-3:] == 'ies' and (word[:-3] + 'y' in org_vocab)\
#             and word.upper() not in const.except_plural_list:
#         temp_org_vocab[word[:-3] + 'y'] = org_vocab[word]
#         temp_org_vocab.pop(word)
#         temp_org_biz[(word[:-3] + 'y').upper()] = org_keyword_biz[word.upper()].copy()
#         temp_org_biz.pop(word.upper())

org_vocab = {word: count for (word, count) in sorted(temp_org_vocab.items(), key=lambda x: x[0])}
# print(org_vocab['fitter'])

with open('Keywords/organic_keyword_vocab.json', 'w') as f:
    json.dump(org_vocab, f)
with open('Keywords/organic_keyword_biz.pkl', 'wb') as f:
    pickle.dump(temp_org_biz, f)

print("if count is 1 and exist in org _vocab in local_vocab, pop it, and then Dumping to loc_keyword")

# print(loc_vocab['fitter'])
for word, count in temp_loc_vocab.copy().items():
    if count == 1 and word in org_vocab:
        temp_loc_vocab.pop(word)
        temp_loc_biz.pop(word.upper())

loc_vocab = {word: count for (word, count) in sorted(temp_loc_vocab.items(), key=lambda x: x[0])}

# print(loc_vocab['fitter'])

with open('Keywords/loc_keyword_vocab.json', 'w') as f:
    json.dump(loc_vocab, f)
with open('Keywords/loc_keyword_biz.pkl', 'wb') as f:
    pickle.dump(temp_loc_biz, f)


print("Integrate location and organic vocabulary into spell keyword vocabulary")

# ------------------ create integrated spell_vocab ----------------------
spell_vocab = loc_vocab.copy()
for word, count in org_vocab.items():
    if word in spell_vocab:
        spell_vocab[word] += count
    else:
        spell_vocab[word] = count

spell_vocab = {word: count for (word, count) in sorted(spell_vocab.items(), key=lambda x: x[0])}

# print(spell_vocab['fitter'])

with open('Keywords/spell_keyword_vocab.json', 'w') as f:
    json.dump(spell_vocab, f)

print(" -------------------------- Memery Occupy Log ------------------------------")
helper.print_memory_occupy(list(locals().items()))
print("-----------------------------------------------------------------------------")
print("---------------------------- End Processing 05 ------------------------------")
print("-----------------------------------------------------------------------------")

