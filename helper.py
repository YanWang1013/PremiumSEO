import json
import re
import linecache
import sys
import numpy as np
# from nltk.corpus import words
from pattern.text.en import singularize, pluralize
from itertools import islice
from math import radians, cos, sin, asin, sqrt


# nltk.download('omw-1.4')


# Helper functions

def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


def json_to_list(txt_json, name):
    if txt_json is not None:
        try:
            dic = json.loads(txt_json)
            if type(dic[name]) is str:
                return dic[name].split()
            if type(dic[name]) is list:
                li = [w for w in flatten(dic[name]) if len(w) != 0]
                if len(li) != 0:
                    li = [w for i in li for w in i.split()]
                    return li
        except Exception as e:
            # print('txt_json', txt_json)
            # print(e)
            # exit(1)
            return [None]

    return [None]


def json_to_list_S(txt_json, name):
    if txt_json is not None:
        try:
            dic = json.loads(txt_json)
            if type(dic[name]) is str:
                return [dic[name]]
            if type(dic[name]) is list:
                return dic[name]
        except Exception as e:
            # print('txt_json', txt_json)
            # print(e)
            # exit(1)
            return [None]
    return [None]


# {"S2": [["DACEYVILLE", "2032"], ["CLOVELLY", "2031"], ["KINGSFORD", "2032"], ["PAGEWOOD", "2035"],
# ["MAROUBRA", "2035"], ["COOGEE", "2034"], ["RANDWICK", "2031"], ["KENSINGTON", "2033"], ["SOUTH COOGEE", "2034"]]}
# Return: ["DACEYVILLE", "CLOVELLY", "KINGSFORD", "PAGEWOOD", ..., "SOUTH COOGEE"]
def json_to_list_S2(txt_json, name):
    if txt_json is not None:
        try:
            dic = json.loads(txt_json)
            if type(dic[name]) is str:
                return [dic[name]]
            if type(dic[name]) is list:
                ret = []
                for val in dic[name]:
                    if type(val) is list:
                        ret.append(val[0])
                if len(ret) > 0:
                    return ret
                else:
                    return dic[name]
        except Exception as e:
            # print('txt_json', txt_json)
            # print(e)
            # exit(1)
            return [None]
    return [None]


def point_to_tuple(point):
    if point is not None:
        coor = tuple([float(d) for d in re.findall('-?[0-9.]*', point) if len(d) != 0])
        if len(coor) == 2:
            return coor


def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}


def number_text(text):
    numbers = 'ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE'.split()
    numeric = list(range(10))
    text = re.findall('(?:' + '|'.join(numbers) + ')*', text)
    text = ' '.join(text)
    text = re.sub('\s+', ' ', text)

    if text == ' ':
        text = ''

    if len(text) != 0:
        for i in numeric:
            text = re.sub(numbers[i], str(i), text)
    return text


def haversine(lat_lon1, lat_lon2):
    try:
        # lat1, lon1, lat2, lon2 = 0, 0, 0, 0
        # if type(lat_lon1) is list:
        #     lat1 = lat_lon1[0]
        #     lon1 = lat_lon1[1]
        # if type(lat_lon2) is list:
        #     lat2 = lat_lon2[0]
        #     lon2 = lat_lon2[1]
        lat1 = lat_lon1[0]
        lon1 = lat_lon1[1]
        lat2 = lat_lon2[0]
        lon2 = lat_lon2[1]

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # print('lat1', lat1)
        # print('lat2', lat2)
        # print('lon1', lon1)
        # print('lon2', lon2)

        # haversine formula
        d_lon = lon2 - lon1
        d_lat = lat2 - lat1

        # print('d_lat', d_lat)
        # print('d_lon', d_lon)

        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return c * r  # returned in terms of kilometers
    except Exception as e:
        print(e)


def haversine_q(lat_lon1, lat_lon2):
    lat1 = lat_lon1[0]
    lat2 = lat_lon2[0]
    lon1 = lat_lon1[1]
    lon2 = lat_lon2[1]

    return abs(lat2 - lat1) * 111 + abs((lon2 - lon1) * cos(radians(lat1)) * 111)


def list_intersect(l1, l2):
    l1 = [l for l in l1 if l is not None]
    l2 = [l for l in l2 if l is not None]
    s1 = set(l1)
    s2 = set(l2)
    return list(s1 & s2)


def cos_mat_v1(array, list_arrays):
    if len(list_arrays) != 0:
        words = [w for w, v in list_arrays]
        vec = [v for w, v in list_arrays]
        null_vec = [1 if len(v) != 0 else 0 for v in vec]
        dum_vec = [v if len(v) != 0 else np.random.normal(0, 1, 50) for v in vec]

        mat = np.array(dum_vec).transpose()

        a = array
        a_t_norm = np.transpose(a) / np.linalg.norm(a)

        dists = np.dot(a_t_norm, mat) * null_vec

        return list(zip(words, dists))
    return [(None, None)]


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


# print memory occupy of variables
def print_memory_occupy(local_vars):
    total_occupy = 0
    for var, obj in local_vars:
        total_occupy += sys.getsizeof(obj)
        if sys.getsizeof(obj) > 1024:
            print(var, sizeof_fmt(sys.getsizeof(obj)))
    print('*** Total ***  ', sizeof_fmt(total_occupy))


# Convert list to dict
def convert_list_to_dict(plist):
    init = iter(plist)
    res_dct = dict(zip(init, init))
    return res_dct


# Get plural of word
def getPlural(word):
    # pl_word = word
    # if word[-3] == 'IES':
    #     pl_word = word[:-3] + 'Y'
    # elif word[-3] == 'ies':
    #     pl_word = word[:-3] + 'y'
    # elif word[-1] == 's':
    #     pl_word = word[:-3] + 'y'
    #
    # elif word[-3:] == 'IES' and (word[:-3] + 'Y') in keywords_vocab:
    #     match_word = word[:-3] + 'Y'
    #     print(word + ' - ' + match_word)
    # if pl_word in const.except_plural_list:
    #     pl_word = word
    try:

        # if word.isalpha() and word in words.words():
        if word.isalpha() and len(word) > 2:
            pl_word = pluralize(word.lower())
        else:
            return word.lower()
    except Exception as e:
        # print(e)
        return word.lower()
    return pl_word


# Get singular of word
def getSingular(word):
    # sl_word = word
    #
    # if word.lower() in const.special_plural_list:
    #     if word == word.upper():
    #         sl_word = const.special_plural_list[word.lower()].upper()
    #     else:
    #         sl_word = const.special_plural_list[word.lower()]
    # elif word.lower() in const.except_plural_list or len(word) < 4:
    #     sl_word = word
    # elif word[-3] == 'IES':
    #     sl_word = word[:-3] + 'Y'
    # elif word[-3] == 'ies':
    #     sl_word = word[:-3] + 'y'
    # # Exception: wives -> wife
    # elif word[-3] == 'VES':
    #     sl_word = word[:-3] + 'F'
    # elif word[-3] == 'ves':
    #     sl_word = word[:-3] + 'f'
    # elif word[-3] == 'SES' or word[-3] == 'ses':
    #     sl_word = word[:-2]
    # elif word[-3] == 'XES' or word[-3] == 'xes':
    #     sl_word = word[:-2]
    # elif word[-2] == 'FS' or word[-2] == 'fs':
    #     sl_word = word[:-1]
    # elif word[-1] == 'S' or word[-1] == 's':
    #     sl_word = word[:-1]
    # else:
    #     sl_word = word
    try:
        # if word.isalpha() and word in words.words():
        if word.isalpha() and len(word) > 3:
            sl_word = singularize(word.lower())
        else:
            return word.lower()
    except Exception as e:
        # print(e)
        return word.lower()
    return sl_word


def getMatchKeyword(jsonDict, keyword, isUpper):
    match_keyword = None
    if isUpper == 'upper':
        pl_keyword = getPlural(keyword).upper()
        sl_keyword = getSingular(keyword).upper()
    else:
        pl_keyword = getPlural(keyword).lower()
        sl_keyword = getSingular(keyword).lower()
    # print('pl_keyword', pl_keyword)
    # print('sl_keyword', sl_keyword)
    if keyword.upper() in jsonDict:
        match_keyword = keyword
        # print('o', match_keyword)
    elif pl_keyword is not None and pl_keyword in jsonDict:
        match_keyword = pl_keyword
        # print('p', match_keyword)
    elif sl_keyword is not None and sl_keyword in jsonDict:
        match_keyword = sl_keyword
        # print('s', match_keyword)
    if match_keyword is not None:
        if isUpper == 'upper':
            match_keyword = match_keyword.upper()
        else:
            match_keyword = match_keyword.lower()
    return match_keyword
