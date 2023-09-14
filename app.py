from flask import Flask, render_template, request, current_app
import requests
from amazon_request import route_ids, data
import folium
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import configparser
from sqlalchemy import create_engine, Column, Text, REAL, Sequence, Float, distinct
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('sqlite:///route.db', echo = True)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///route.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Session = sessionmaker(bind = engine)
session = Session()
config = configparser.ConfigParser()
config.read("config.ini")
api_key = config['api_info']["api_key"]
destination_lat = None
destination_lng = None
stop_lat = None
stop_lng = None
url = config['api_info']['base_url']
conn = sqlite3.connect("route.db")
c = conn.cursor()
datakeys = route_ids() #datakeys is a list
singlecitywithstops = []    
city_list = []
state_list = []
place = [] 
all_stats = None
r = requests.get(url)
json_data = r.json()



def plugging_it_in(destination_lat, destination_lng, stop_lat, stop_lng, api_key):
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?destinations={destination_lat},{destination_lng}&origins={stop_lat},{stop_lng}&units=imperial&key={api_key}'
    return url


Base = declarative_base()
class table(Base):
    __tablename__ = "routes"
    id = Column(Text, primary_key= True)
    route_id = Column(Text)
    stop_id = Column(Text)
    stop_lat = Column(Float)
    stop_lng = Column(Float)
    route_sq = Column(Text)
    city = Column(Text)
    other = Column(Text)

    def __init__(self, id, route_id, stop_id, stop_lat, stop_lng, route_sq, city, other):
        self.id = id
        self.route_id = route_id
        self.stop_id = stop_id
        self.stop_lat = stop_lat
        self.stop_lng = stop_lng
        self.route_sq = route_sq
        self.city = city
        self.other = other

    def __str__(self):
        return f"Routes {self.route_id}"



def grab_cities():
    with current_app.app_context():
                # coordinates = session.query(table).filter_by(route_id = str_route_ess).all()

        unique_cities = session.query(table.city).distinct().all()
        cities = [city[0] for city in unique_cities]
    return cities

def insert_from_aws():
    for route_id in datakeys:
        route_data = data[route_id]        
        # Insert or update stops for the route
        for stop_id, stop_info in route_data["stops"].items():
            # Initialize the 'table' class with the required parameters
            stop = table(id = route_id + stop_id, route_id=route_id, stop_id=stop_id, stop_lat=(stop_info['lat']), stop_lng=(stop_info['lng']), route_sq=None, city=None, other = None)
            session.add(stop)
        # Commit changes to the database after processing each route
        session.commit()
    session.close()


def insert_google():

    c.execute('Select stop_lat, stop_lng FROM routes') 
    row = c.fetchall()
    for i in range(len(row) - 1):
        stop_lat, stop_lng = row[i]
        destination_lat, destination_lng = row[i+1]
        url = (plugging_it_in(destination_lat, destination_lng, stop_lat, stop_lng, api_key))  
        r = requests.get(url)
        json_data = r.json()
        supposed_city = json_data['origin_addresses'][0].split(',')[1]
        c.execute("update routes set other = ? where stop_lat = ? and stop_lng = ?",(supposed_city, stop_lat, stop_lng))
        conn.commit()
        
    c.close()


def create_map(name_of_route):
    feature_group = folium.FeatureGroup("Locations")
    m = folium.Map(location =[47.2529, -122.4443], zoom_start = 12)
    map_coordinates = session.query(table).filter_by(route_id = name_of_route).all()
    for stop in map_coordinates:
        name = stop.stop_id
        lat = stop.stop_lat
        lng = stop.stop_lng

        feature_group.add_child(folium.Marker(location= [lat, lng], popup = name))
    
    m = folium.Map(location =[lat, lng], zoom_start = 14)

    m.add_child(feature_group)
    m.save('map.html')

@app.route('/', methods = ['POST', 'GET'])
def dropdown():   
    if request.method == 'POST':
        str_route = (request.get_data().decode()) #get_data is a function from flask.
        str_route_ess = (str_route[5:49]) #this is the route id without the data= and stuff.
        coordinates = session.query(table).filter_by(route_id = str_route_ess).all()
        total_distance = 0.0
        final_time = 0.0
        stopcounter = 0
        for i in range(len(coordinates) - 1):
            source_lat = coordinates[i].stop_lat
            source_lng = coordinates[i].stop_lng
            destination_lat = coordinates[i + 1].stop_lat
            destination_lng = coordinates[i + 1].stop_lng
            response = requests.get(plugging_it_in(destination_lat, destination_lng, source_lat, source_lng, api_key))
            data = response.json()
            distance = data["rows"][0]["elements"][0]["distance"]["text"]
            time = data["rows"][0]['elements'][0]["duration"]['text']
            final_time += int(time.split()[0])
            stopcounter += 1
            if 'ft' in distance:
                ft_converted = float(distance.split()[0])/5280 #convert to mile
                total_distance += ft_converted
            else:
                mi_converted = float(distance.split()[0])
                total_distance += mi_converted
            final_formatted_time = str(round(final_time/60, 2)) + " hours"
            final_distance =  str(round(total_distance, 2)) + " miles"
            

        db.session.commit()



        create_map(str_route_ess) #need this here to generate a new map when selecting new location.

        return render_template("index.html", final_distance = final_distance, final_time = final_formatted_time, number_of_stops = stopcounter, str_route_ess = str_route_ess, data= data,  datakeys = datakeys)  
    return render_template("index.html", datakeys = datakeys)


@app.route('/city', methods = ['POST', 'GET'])
def search_by_city():
    cities = grab_cities()
    selected_city_full = None
    getting_routes = None
    route_result = []
    
    if request.method == "POST":
        selected_city_full = request.form.get('city')
        getting_routes = session.query(table).filter_by(city = selected_city_full).distinct().all()
        for route in getting_routes:
            if route.route_id not in route_result:
                route_result.append(str(route.route_id))
        print(api_key)
        return render_template("city.html", cities = cities, city_in_question = selected_city_full, routes = route_result)
    return render_template("city.html", cities = cities, city_in_question = selected_city_full, routes = route_result)


if __name__ == '__main__':
    # Base.metadata.create_all(engine)
    app.run(debug = True)

    
    

# datakeys are  the routeID titles
# have to open map.html in liveserver first.