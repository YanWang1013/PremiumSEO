import pickle
import json

from difflib import SequenceMatcher
import const as const
import helper as helper

print(helper.getSingular('inci'))
print(helper.getSingular('aaae'))
# print(helper.getPlural('aa'))
exit(1)



with open('Keywords/organic_temp_keyword_vocab.json', 'r') as f:
    temp_keywords_vocab = json.load(f)
with open('Keywords/organic_temp_keyword_biz.pkl', 'rb') as f:
    temp_organic_keyword_biz = pickle.load(f)

# word = 'slogan'
# keywords_vocab = {}
# for word, count in temp_keywords_vocab:
#
#     candidates = {}
#     for vocab_w in list(keywords_vocab)[-40:]:
#         score = SequenceMatcher(None, vocab_w, word).ratio()
#         print(vocab_w, score)
#         if score > const.SequenceMatcher_LowerLimit:
#             candidates[vocab_w] = score
#             exit(1)
#
#     if len(candidates) == 0:
#         keywords_vocab[word] = count
# exit(1)
# with open('Keywords/organic_keyword_vocab.json', 'r') as f:
#     keywords_vocab = json.load(f)
# print(keywords_vocab['fitter'])
# exit(1)
# with open('Keywords/organic_keyword_biz.pkl', 'rb') as f:
#     organic_keyword_biz = pickle.load(f)
# print(organic_keyword_biz['SITTER'])
# exit(1)

temp4w_counting = {}

organic_keyword_biz = {}
keywords_vocab = {}

print('temp_keywords_vocab length', len(temp_keywords_vocab))
stop_count = 0
for word, count in temp_keywords_vocab:
    if stop_count > 100:
        break
    candidates = {}
    # print(list(keywords_vocab)[-40:])
    # exit(1)
    for vocab_w in list(keywords_vocab)[-40:]:
        score = SequenceMatcher(None, vocab_w, word).ratio()
        if score > const.SequenceMatcher_LowerLimit and \
                (vocab_w not in const.except_plural_list and word not in const.except_plural_list):
            candidates[vocab_w] = score
            # print('word', word, 'count', count)
            # print('score', score)
            # print('vocab_w', vocab_w)
            # print(keywords_vocab)
    print('candidates', candidates)
    if len(candidates) == 0:
        organic_keyword_biz[word] = temp_organic_keyword_biz[word]
        keywords_vocab[word] = count
        temp4w_counting[word] = count
    else:

        stop_count += 1
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
            # print('--- why pop ---')
            # print('word', word)
            # print('replaced', replaced, 'count', count)
            # print('temp4w_counting', temp4w_counting[word])
            # print(keywords_vocab)
            # print(organic_keyword_biz)
            # print(temp4w_counting)
            # exit(1)
        else:
            # organic_keyword_biz[replaced] += temp_organic_keyword_biz[word]
            for t in temp_organic_keyword_biz[word]:
                if t not in organic_keyword_biz[replaced]:
                    organic_keyword_biz[replaced][t] = ''

            temp4w_counting[replaced] += count

print(keywords_vocab['ABORIGINAL'])

# remove -s, -ies
temp = keywords_vocab.copy()
for word in temp:
    match_word = None
    if word[-1] == 'S' and word[:-1] in keywords_vocab and word not in const.except_plural_list:
        match_word = word[:-1]
        # if word == 'LEAKS':
        print(word + ' - ' + match_word)

    elif word[-3:] == 'IES' and (word[:-3] + 'Y') in keywords_vocab:
        match_word = word[:-3] + 'Y'
        print(word + ' - ' + match_word)

    if match_word is not None:
        # print(match_word)
        # exit(1)
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

keywords_vocab = {word.lower(): temp4w_counting[word] for word in sorted(keywords_vocab) if temp4w_counting[word] > 2}

print(keywords_vocab['LEAKS'])

print("End Processing")
