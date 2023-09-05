import requests
response = requests.get('https://s3.us-west-2.amazonaws.com/amazon-last-mile-challenges/almrrc2021/almrrc2021-data-evaluation/model_apply_inputs/eval_route_data.json')




#google api
api_key = "AIzaSyDYt_0UslO8mFS6GqNm0Zx9v9liGj6Oa6U"
url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
r = requests.get(url+ "origins=" + "&destinations="  + "&key=" + api_key)



data = response.json()
result = {}


def route_ids():
    datakeys = list(data.keys())[1:11]  #[:10] to limit number of routes we present to 10
    return datakeys

def get_stats(user_key_request):
    return data[user_key_request]
