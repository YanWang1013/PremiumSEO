stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
             "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
             'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
             'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
             'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
             'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
             'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
             'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
             'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
             't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're',
             've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',
             "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
             "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
             "weren't", 'won', "won't", 'wouldn', "wouldn't",
             'near', 'nearest', 'in', 'around', 'within', 'someplace', 'somewhere']
# "australia", "st", "street", "rd", "road", "district", "building", "postcode", "city", "town", "suburbs", "suburb",
# "urban", "state" ]
stopwords = {k.upper(): '' for k in stopwords}

digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

pose_keywords = {'TOWN': 6, 'URB': 5, 'ST': 4, 'NUMBER': 3, 'HOUSE': 2, 'POSTCODE': 1, 'STATE': 0}

loc_keyword_pose = {
    'TOWN': 'TOWN', 'CITY': 'TOWN',  # 6
    'URBAN': 'URB', 'URB': 'URB',  # 5
    'STREET': 'ST', 'ST': 'ST', 'RD': 'ST', 'ROAD': 'ST', 'AVE': 'ST', 'DR': 'ST', 'WAY': 'ST', 'CL': 'ST',
    'CRES': 'ST', 'PARADE': 'ST', 'TRACK': 'ST', 'HWY': 'ST', "TERRACE": 'ST', 'PL': 'ST',  # 4
    'HOUSE NUMBER': 'NUMBER', 'HOME NUMBER': 'NUMBER', 'BUILDING NUMBER': 'NUMBER',  # 3
    'HOUSE': 'HOUSE', 'HOME': 'HOUSE',  # 2
    'POST CODE': 'POSTCODE', 'POSTCODE': 'POSTCODE',  # 1
    'STATE': 'STATE'  # 0
}

# populate_search_words = {'SERVICE', 'HOME', 'STORE', 'COMPANY', 'SHOP', 'LTD', 'PTY', 'DESIGN', 'FOOD', 'PLACE',
# 'CENTRE', 'INTEREST', 'CONSTRUCTION', 'SALONS', 'PLANNING', 'AGENCY', 'CONSULTANT', 'RESTAURANT', 'SUPPLIER',
# 'TRADESPERSON', 'DECORATION', 'GENERAL', 'CONTRACTOR', 'ELECTRICAL', 'PERSONAL', 'REPAIR', 'FASHION', 'ELECTRICS',
# 'VACANCES', 'CENTER', 'GOODS', 'INTERIOR', 'TRAINING', 'WORKSHOP', 'CARE', 'EQUIPMENT', 'SCHOOL', 'RELAXATION',
# 'MARKETING', 'SUPPLY', 'THERAPIST', 'WOOD', 'CLINIC', 'ARTS', 'HOUSEKEEPINGS', 'FACILITIY', 'AGENT', 'AUTO',
# 'COURSES', 'CITY', 'AGENT', 'PRODUCTS', 'ADVERTISING', 'DIALER', 'OFFICE', 'COFFEE', 'CAFE', 'ARCHITECTURE',
# 'RENTAL', 'HEALTH', 'CAR', 'BEAUTY', 'DR', 'INDUSTRY', 'INDUSTRIES', 'CLOTHING', 'BAR', 'PARK', 'HAIR', 'ESTATE',
# 'ENERGY', 'PETS', 'MANAGEMENT', 'MEDIA'}

populate_search_words = {'SOUTH': '', 'ST': '', 'SERVICE': '', 'NEW': '', 'NORTH': '', 'GENERAL': '', 'AUSTRALIA': '',
                         'EAST': '', 'WEST': ''}

PREMIUM_BIZ_SCORE = 1000
PREMIUM_LOC_SCORE = 100

PREMIUM_DEMO_SCORE = 10
PREMIUM_PREM_SCORE = 1

except_plural_list = {'leaks'}
# except_plural_list = {}
special_plural_list = {'wife': 'wives', 'roof': 'roofs', 'belief': 'beliefs', 'chef': 'chefs', 'chief': 'chiefs'}

# except_town_list = {'ARGYLE': '', 'COLES': ''}
except_town_list = {}

SequenceMatcher_LowerLimit = 0.889
