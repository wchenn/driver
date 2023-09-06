from flask import Flask, render_template, request
import requests
from amazon_request import route_ids, data
import folium
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from configparser import ConfigParser
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Text, REAL, Sequence, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('sqlite:///route.db', echo = True)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

Session = sessionmaker(bind = engine)
session = Session()

config_object = ConfigParser()
config_object.read("config.ini")
api_stuff = config_object["api_info"]
api_key = api_stuff["api_key"]
url = api_stuff["url"]
conn = sqlite3.connect("route.db")
c = conn.cursor()
datakeys = route_ids() #datakeys is a list
singlecitywithstops = []    
city_list = []
state_list = []
place = [] 
# str_route = (request.get_data().decode())
# str_route_ess = (str_route[5:49])
# all_stats = (data[str_route_ess]) 
source = ''
destination = ''
# r = requests.get(url+ "origins=" + source + "&destinations=" + destination + "&key=" + api_key)
# json_data = r.json()
# stat = data[curr_route] #used to pull from the s3





Base = declarative_base()
class table(Base):
    __tablename__ = "routes"
    route_id = Column(Integer, primary_key=True)
    route_number = Column(Integer, Sequence('route_number_seq'), unique=True)
    stop_id = Column(Text)
    stop_lat = Column(Float)
    stop_lng = Column(Float)
    route_sq = Column(Text)
    city = Column(Text)

    def __init__(self, route_id, stop_id, stop_lat, stop_lng, route_sq, city):
        self.route_id = route_id
        self.stop_id = stop_id
        self.stop_lat = stop_lat
        self.stop_lng = stop_lng
        self.route_sq = route_sq
        self.city = city



def insert_from_aws():
    for route_id in datakeys:
        route_data = data[route_id]        
        # Insert or update stops for the route
        for stop_id, stop_info in route_data["stops"].items():
            # Initialize the 'table' class with the required parameters
            stop = table(route_id=route_id, stop_id=stop_id, stop_lat=(stop_info['lat']), stop_lng=(stop_info['lng']), route_sq=None, city=None)
            session.add(stop)
        # Commit changes to the database after processing each route
        session.commit()

    # Close the session at the end
    session.close()

        

# def insert_google():
#     records = session.query(table.stop_lat, table.stop_lng).all()
#     for stop_lat, stop_lng in records:
#         print(stop_lng, stop_lat)


# def populate_drop():
    
#     for i in range(len(datakeys)):
#         curr_route = datakeys[i]
#         c.execute("INSERT INTO city (routeid) VALUES (curr_route) VALUES (?)", (curr_route))
#         for destinations in stat['stops'].values():
#             singlecitywithstops.append(str(destinations['lat']) + ", " +str(destinations['lng']) +"|")
#         for i in range(0, len(singlecitywithstops) -2, 2):
#             source = singlecitywithstops[i]
#             destination = singlecitywithstops[i+2]
#         conn.commit()
#         conn.close()
           
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
            destination_address  = json_data['destination_addresses'][0]
            cities = destination_address.split(', ')[1]
            state = destination_address.split(', ')[2].split(' ')[0]
            if state not in state_list:
                state_list.append(state)
            if cities not in city_list:
                city_list.append(str(cities))
            mile = json_data['rows'][0]['elements'][0]['distance']['text'] # this is for mileage. all mileage is a str.
            if 'ft' in mile:
                ft_converted = float(mile.split()[0])/5280 #turning ft into miles
                distance += ft_converted
            else:
                mi_converted = float(mile.split()[0])
                distance += mi_converted
            minutes = json_data['rows'][0]['elements'][0]['duration']['text']#this is for time
            formatted_minute = float(minutes.split()[0])
            time += formatted_minute
            hours = time / 60

        final_distance = str(round(distance, 2)) + " miles"
        final_time = str(round(hours, 2)) + " hours"

    
        create_map() #need this here to generate a new map when selecting new location.
        return render_template("index.html", final_distance = final_distance, final_time = final_time, datakeys = datakeys, all_stats = all_stats['station_code'], number_of_stops = number_of_stops, city_list = city_list, state_list = state_list, str_route_ess = str_route_ess)  

    return render_template("index.html", datakeys = datakeys)  

# def create_table(conn, create_table_sql):
#     """ create a table from the create_table_sql statement
#     :param conn: Connection object
#     :param create_table_sql: a CREATE TABLE statement
#     :return:
#     """
#     try:
#         c = conn.cursor()
#         c.execute(create_table_sql)
#     except Error as e:
#         print(e)



if __name__ == '__main__':
    # sqlstuff()
    # create_table(conn, table)
#    Base.metadata.create_all(engine)
    # print('done with aws insert, google now')
    insert_from_aws()
    # print('done with google insert')
        # app.run(debug = True)
    # create_map()
    
    

# datakeys are  the routeID titles
# have to open map.html in liveserver first.