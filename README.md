# SpecialcodeQF_ML
 Commercial Search Engine based on location and premium
# Keywords
Python, Flask, Numpy, Pandas, Natural Languange Processing

# ToDo
An example of the network URL called from the client to the server is:

http://127.0.0.1:8000/api/search_engine?query=jb+hi+fi&lat=-33.867916580953&long=151.22363461744&radius=4&topN=1000&page=1

There are 6 variables: query, lat, lon, radius, topN and page.
Query is the input string, latitude and longitude are the coordinates, radius and topN are not significant variables but they are the optimal values to search within i.e. radius of 4km of location searched and find 1000 businesses. Page is an important variable because the variable tells the code to return only a portion of the businesses depending on which page the user is on.

When the user searches for the first time - it automatically loads page 1. per page you would have 9 businesses, but on the first page you have 8 businesses - 8 businesses + 1 AVAILABLE (for selling purposes). That means that if page=1, return businesses ranked 1st-8th, if page=2, return businesses ranked 9th-17th, if page=3, return businesses ranked 18th-26th, if page=4, return businesses ranked 27th-35th, and so forth.

Latitude and longitude are coordinate variables taken from the client. Query is the string taken from the user’s search. The query is broken down into 2 main categories – location keywords (suburb keywords, region keywords, postcode keywords, etc), and non-location keywords (or non-loc keywords, like trade keywords, business keywords, etc).

# Cronjob -

Cronjob.py is executed manually (automatically on the production environment). The main roles of it is to “download” the tables from the server (META_DATA_index_copy, au_towns, etc) and transform into a .pkl file. It normally takes within an hour as a whole depending on the size of the tables. It simply executes 8 python files which organises keywords from the tables above into its respective vectors. If you see the need to edit those files, please make a copy of them and make the appropriate adjustments in cronjob.py (commenting what you did) so I can have a look at it.

