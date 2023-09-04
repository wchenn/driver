import requests
response = requests.get('https://s3.us-west-2.amazonaws.com/amazon-last-mile-challenges/almrrc2021/almrrc2021-data-evaluation/model_apply_inputs/eval_route_data.json')

data = response.json()
result = {}


def route_ids():
    datakeys = list(data.keys())[1:11]  #[:10] to limit number of routes we present to 10
    return datakeys

def get_stats(user_key_request):
    return data[user_key_request]

# def get_station_code(user_key_request):
#     station_code = data[user_key_request]['station_code']
#     return station_code

# def get_departure_time(user_key_request):
#     departure_time = data[user_key_request]['departure_time_utc']
#     return departure_time 

# def get_stops(user_key_request):
#     stops= data[user_key_request]['stops']
#     return stops


# def get_station_code():
#     for routeid, info in list(data.items())[:10]:
#         result[routeid] = {"Station code": info.get("station_code")}
#     return result

# def get_departure_time():
#     for routeid, info in list(data.items())[:10]:
#         result[routeid] = {"Departure Time": info.get("departure_time_utc")}
#     return result

# def get_stops():
#     for routeid, info in data.items():
#         result[routeid] = {"Stops: ": info.get("stops")}
#     return result

# def get_stop_location():
#     location = {}
#     for routeid, info in data.items():
#         result[routeid] = {"Stop ID": info.get("stops")}
#         for inital, stop_info in info["stops"].items():
            
#             lat = stop_info["lat"]
#             lng = stop_info['lng']
        
#             location[inital] = {
#                 "lat": lat, "lng": lng
#             }
#         result[routeid] = {'stops': location}
#     return result
        # result[routeid] = {"Initial":}
        # stop_locations = {}
        # for stops in info[""]
