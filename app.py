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
conn = sqlite3.connect("city.db")
cursor = conn.cursor()
r = requests.get(url+ "origins=" + "&destinations="  + "&key=" + api_key)
datakeys = route_ids() #datakeys is a list
singlecitywithstops = []    
city_list = []
state_list = []
place = [] 
str_route = (request.get_data().decode())
str_route_ess = (str_route[5:49])
all_stats = (data[str_route_ess]) 
json_data = r.json()
stat = data[curr_route] #used to pull from the s3



def populate_drop():
  
    for i in range(len(datakeys)):
        curr_route = datakeys[i]
        for destinations in stat['stops'].values():
            singlecitywithstops.append(str(destinations['lat']) + ", " +str(destinations['lng']) +"|")
        for i in range(0, len(singlecitywithstops) -2, 2):
            source = singlecitywithstops[i]
            destination = singlecitywithstops[i+2]
        conn.commit()
        conn.close()
           

def create_map():
    feature_group = folium.FeatureGroup("Locations")
    for name, stop_details in all_stats['stops'].items():
        lat = stop_details['lat']
        long = stop_details['lng']
        feature_group.add_child(folium.Marker(location= [lat, long], popup = name))
    
    m = folium.Map(location =[lat, long], zoom_start = 14)

    m.add_child(feature_group)
    m.save('map.html')

@app.route('/', methods = ['POST'])
def dropdown():   
    if request.method == 'POST':
        number_of_stops = len(all_stats['stops'])
        time = 0
        distance = 0
        for destinations in all_stats['stops'].values():
            place.append(str(destinations['lat']) + ", " + str(destinations['lng']) + '|')


        for i in range(0, len(place) -2 , 2 ):
            source = place[i]
            destination = place [i+2]
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