from flask import Flask, render_template, request
from amazon_request import get_departure_time, get_station_code, get_stops, route_ids, data
import folium

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
        all_stats = (data[str_route_ess])
        create_map()
        return render_template("index.html", datakeys = datakeys, all_stats = all_stats)  

    return render_template("index.html", datakeys = datakeys)  


@app.route('/time')
def run_get_departure_time():
    data = get_departure_time()
    return render_template("index.html", data = data)

@app.route('/station')
def run_get_station_code():
    data = get_station_code()
    return render_template("index.html", data = data)

# @app.route('/locations')
# def run_get_stop_location():
#     data = get_stop_location()
#     return render_template("index.html", data = data)


@app.route('/stop')
def run_get_stops():
    data = get_stops()
    return render_template("index.html", data = data)



if __name__ == '__main__':
    app.run(debug = True)
    create_map()
    

# datakeys are  the routeID titles,