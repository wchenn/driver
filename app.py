from flask import Flask, render_template, request
from amazon_request import route_ids, data
import folium
import requests

app = Flask(__name__)




def create_map():
    feature_group = folium.FeatureGroup("Locations")
    # m = folium.Map(location =[47.2529, -122.4443], zoom_start = 12)
    for name, stop_details in all_stats['stops'].items():
        lat = stop_details['lat']
        long = stop_details['lng']
        feature_group.add_child(folium.Marker(location= [lat, long], popup = name))
    
    m = folium.Map(location =[lat, long], zoom_start = 13)

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
        api_key = 'AIzaSyDYt_0UslO8mFS6GqNm0Zx9v9liGj6Oa6U'
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
        place = [] 
        time = 0
        distance = 0
        counter = 0
        for destinations in all_stats['stops'].values():
            place.append(str(destinations['lat']) + ", " + str(destinations['lng']) + '|')


        for i in range(0, len(place) -2 , 2 ):
            source = place[i]
            destination = place [i+2]

            r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
            response_data = r.json()
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
            counter += 1

        final_distance = str(round(distance, 2)) + " miles"
        final_time = str(round(hours, 2)) + " hours"

    
        create_map() #need this here to generate a new map when selecting new location.
        return render_template("index.html", final_distance = final_distance, final_time = final_time, datakeys = datakeys, all_stats = all_stats, counter = counter)  

    return render_template("index.html", datakeys = datakeys)  




if __name__ == '__main__':
    app.run(debug = True)
    create_map()
    

# datakeys are  the routeID titles
# have to open map.html in liveserver first.