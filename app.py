from flask import Flask, render_template, request
from amazon_request import get_departure_time, get_station_code, get_stops, route_ids, data

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def dropdown():
    datakeys = route_ids()
    if request.method == 'POST':
        str_route = (request.get_data().decode())
        str_route_ess = (str_route[5:49])
        all_stats = (data[str_route_ess])
        print(all_stats)
    return render_template("index.html", datakeys = datakeys, all_stats = all_stats)  

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
    