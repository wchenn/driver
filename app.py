from flask import Flask, render_template
from amazon_request import get_departure_time, get_station_code, get_stop_location, get_stops

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/time')
def run_get_departure_time():
    data = get_departure_time()
    return render_template("index.html", data = data)

@app.route('/station')
def run_get_station_code():
    data = get_station_code()
    return render_template("index.html", data = data)

@app.route('/locations')
def run_get_stop_location():
    data = get_stop_location()
    return render_template("index.html", data = data)


@app.route('/stop')
def run_get_stops():
    data = get_stops()
    return render_template("index.html", data = data)




if __name__ == '__main__':
    app.run(debug = True)