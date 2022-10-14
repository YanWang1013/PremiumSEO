import mysql.connector

mydb = mysql.connector.connect(
    host="167.99.28.217",
    user="myuser",
    passwd="mypass",
    database="new_db"
)

from math import radians, cos, sin, asin, sqrt


def distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


mycursor = mydb.cursor(buffered=True)
mycursor1 = mydb.cursor(buffered=True)

mycursor.execute("SELECT id, latitude, longitude, name from au_towns;")
mycursor1.execute("SELECT id, latitude, longitude, name from au_towns ORDER by id ASC;")
myresult = mycursor.fetchall()
myresult1 = mycursor1.fetchall()

refixed = []

print("X")
live_track = 0
total_results = []


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


whole_count = 0

for X in myresult:
    live_track = live_track + 1
    whole_count = whole_count + 1
    # print(live_track)
    if live_track == 200 or whole_count >= len(myresult) - 1:
        try:
            mycursor1.executemany('UPDATE au_towns SET nearest = %s WHERE id = %s', total_results)
            mydb.commit()
        except Exception as e:
            print(e)
            print("big error")
            break
        total_results = []
        live_track = 0
        print(total_results)

    id = X[0]
    x = X[1]
    y = X[2]
    print(id, x, y, X[3])
    counter = {"nearest": 99999, "id": id}
    for Y in myresult1:
        if id == Y[0]:
            pass
        else:
            temp = distance(x, y, Y[1], Y[2])
            if temp < counter["nearest"]:
                counter["nearest"] = temp
    counter["nearest"] = truncate(counter["nearest"], 5)
    print(counter["nearest"], counter["id"])
    total_results.append((counter["nearest"], counter["id"]))

print(distance(-33.92513, 151.21320, -33.92492, 151.22781))
