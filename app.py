from flask import Flask, render_template, request
from amazon_request import route_ids, data
import folium
import requests
from flask_sqlalchemy import SQLAlchemy
import json
import sqlite3
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
api_key = "AIzaSyDYt_0UslO8mFS6GqNm0Zx9v9liGj6Oa6U"
url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
conn = sqlite3.connect("city.db")
cursor = conn.cursor()

# class Routes(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     routeid = db.Column(db.String(150))
#     citieslist = db.Column(db.string(150))

#     def __repr__(self):
#         return f"{self.routeid} - {self.citieslist}"


# from sqlalchemy import create_engine, Table, Column, TEXT, MetaData, JSON
# from sqlalchemy.dialects.postgresql import JSONB, insert

# def sqlstuff():
#     engine = create_engine('postgresql://postgres:7751@localhost:5432/routes')
#     metadata = MetaData()
#     metadata.reflect(bind = engine)

#     routes = Table('routes', metadata,
#                 Column('id', TEXT , primary_key = True),
#                 Column('city', JSONB),
#                 extend_existing= True
#                 )

#     metadata.create_all(engine)

#     table_name = 'routes'
#     table = metadata.tables[table_name]
#     r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
#     response_data = r.json()
#     datakeys = route_ids()
#     for i in range(len(datakeys)):
#         curr_route = datakeys[i]
#         inserting_route = insert(routes).values(id = curr_route)
#         conn = engine.connect()
#         conn.execute(inserting_route)
#         conn.commit()
#     print(table.__repr__())



def populate_drop():
    other_drop =[]
    datakeys = route_ids() #datakeys is a list
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes( routeid TEXT, cities TEXT)''')
    cursor.execute('''INSERT INTO routes (routeid, cities) VALUES (?, ?)''', (datakeys))
    conn.commit()
    conn.close()
    singlecitywithstops = []
    citylist = []
    source = ""
    destination = ""
    r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)

    json_data = r.json()
    
    
    for i in range(len(datakeys)):
        datakeys = route_ids()
        curr_route = datakeys[i]
        # cursor.execute('''INSERT INTO routes (routeid, cities) VALUES (?, ?)''', tuple(datakeys[i]))
        # conn.commit()
        # conn.close()
        stat = data[curr_route]
        for destinations in stat['stops'].values():
            singlecitywithstops.append(str(destinations['lat']) + ", " +str(destinations['lng']) +"|")
        for i in range(0, len(singlecitywithstops) -2, 2):
            source = singlecitywithstops[i]
            destination = singlecitywithstops[i+2]
            r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
            json_data = r.json()
            result = json_data
            # result = json_data['destination_addresses'][0].split(", ")[1]
            print(result)
            # if result not in citylist:
            #     has_number = any(char.isnumeric() for char in result)
            #     if not has_number:
            #         citylist.append(result)
    # print(citylist)

        # for i in range(0, len(place) -2 , 2 ):
        #     source = place[i]
        #     destination = place [i+2]

        #     r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
        #     response_data = r.json()

#             destination_address  = response_data['destination_addresses'][0]
#             cities = destination_address.split(', ')[1]
# thinking about making a dropdown with all the cities, chooose and select and will return routes that include that city



def create_map():
    feature_group = folium.FeatureGroup("Locations")
    for name, stop_details in all_stats['stops'].items():
        lat = stop_details['lat']
        long = stop_details['lng']
        feature_group.add_child(folium.Marker(location= [lat, long], popup = name))
    
    m = folium.Map(location =[lat, long], zoom_start = 14)

    m.add_child(feature_group)
    m.save('map.html')

@app.route('/', methods = ['GET', 'POST'])
def dropdown():   
    datakeys = route_ids()
    if request.method == 'POST':
        str_route = (request.get_data().decode())
        str_route_ess = (str_route[5:49])
        global all_stats
        all_stats = (data[str_route_ess])  # all stats are all of the stats of the route selected. 
        place = [] 
        number_of_stops = len(all_stats['stops'])
        time = 0
        distance = 0
        city_list = []
        state_list = []
        for destinations in all_stats['stops'].values():
            place.append(str(destinations['lat']) + ", " + str(destinations['lng']) + '|')


        for i in range(0, len(place) -2 , 2 ):
            source = place[i]
            destination = place [i+2]

            r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
            response_data = r.json()
            destination_address  = response_data['destination_addresses'][0]
            cities = destination_address.split(', ')[1]
            state = destination_address.split(', ')[2].split(' ')[0]
            if state not in state_list:
                state_list.append(state)
            if cities not in city_list:
                city_list.append(str(cities))
            mile = response_data['rows'][0]['elements'][0]['distance']['text'] # this is for mileage. all mileage is a str.
            if 'ft' in mile:
                ft_converted = float(mile.split()[0])/5280 #turning ft into miles
                distance += ft_converted
            else:
                mi_converted = float(mile.split()[0])
                distance += mi_converted
            minutes = response_data['rows'][0]['elements'][0]['duration']['text']#this is for time
            formatted_minute = float(minutes.split()[0])
            time += formatted_minute
            hours = time / 60

        final_distance = str(round(distance, 2)) + " miles"
        final_time = str(round(hours, 2)) + " hours"

    
        create_map() #need this here to generate a new map when selecting new location.
        return render_template("index.html", final_distance = final_distance, final_time = final_time, datakeys = datakeys, all_stats = all_stats['station_code'], number_of_stops = number_of_stops, city_list = city_list, state_list = state_list, str_route_ess = str_route_ess)  

    return render_template("index.html", datakeys = datakeys)  




if __name__ == '__main__':
    # sqlstuff()
    populate_drop()

    # app.run(debug = True)
    # create_map()
    

# datakeys are  the routeID titles
# have to open map.html in liveserver first.