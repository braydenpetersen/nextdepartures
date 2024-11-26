from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import math
from datetime import datetime
import json

# app instance
app = Flask(__name__)
CORS(app)

load_dotenv() # get environment variables

# get the environment variables
API_KEY = os.getenv('API_KEY')
LAT = os.getenv('LAT') 
LON = os.getenv('LON')
MAX_DISTANCE = os.getenv('MAX_DISTANCE')

def load_stop_code_mapping():
    with open('static/stop_code_to_platform.json', 'r') as f:
        return json.load(f)
    
def check_ring_road(platform, routeNumber, routeNetwork):
    if (routeNumber == '30' and (platform == '5' or routeNetwork == 'GO Transit')) or \
       (routeNumber == '19' and platform == '4') or \
       (routeNumber == '9' and platform == '6'):
        return True
    if routeNumber not in ['30', '19', '9']:
        return True
    return False

def remove_station(headsign):
    return headsign.replace("Station", "").strip()

# api/test
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Hello from the server!',
    })

# api/departures
@app.route('/api/departures', methods=['GET'])
def get_departures():

    payload = {
        'lat': LAT,
        'lon': LON,
        'max_distance' : MAX_DISTANCE
    }

    headers = {
        'apiKey' : API_KEY
    }

    # get the data from the API
    response = requests.get('https://external.transitapp.com/v3/public/nearby_routes', headers=headers, params=payload)
    data = response.json()

    departures_list = []

    stop_code_to_platform = load_stop_code_mapping()
    
    # Iterate over the routes
    for route in data.get('routes', []):

        routeNumber = route['route_short_name']
        routeColor = f"#{route['route_color']}"
        routeTextColor = f"#{route['route_text_color']}"
        routeNetwork = route['route_network_name']

        # Iterate over the itineraries within a route
        for itinerary in route.get("itineraries", []):

            headsign = remove_station(itinerary['direction_headsign'])
            stop_code = itinerary['closest_stop']['stop_code']

            platform = stop_code_to_platform.get(stop_code, "?")

            is_first_departure = True

            # Iterate over the departure schedule items within an itinerary
            for departure in itinerary.get("schedule_items", []):
                time = datetime.fromtimestamp(departure['departure_time']).strftime('%H:%M')
                current_time = datetime.now()
                departure_datetime = datetime.fromtimestamp(departure['departure_time'])
                time_until_departure = (departure_datetime - current_time).total_seconds() // 60

                if time_until_departure < 10:
                    time = f"{int(time_until_departure)} min"

                # assign branch code if first departure
                branch_code = itinerary['branch_code'] if is_first_departure else ""

                countdown = max(0, math.floor(time_until_departure))

                # # special case for Routes 30 and 9, only one stop code is valid (same buses)
                if routeNumber == '30' and routeNetwork == "GRT":
                    headsign = 'Ring Road'
                
                if check_ring_road(platform, routeNumber, routeNetwork):
                    departure_item = {
                        'routeNumber': routeNumber,
                        'routeColor': routeColor,
                        'routeTextColor': routeTextColor,
                        'routeNetwork': routeNetwork,
                        'headsign': headsign,
                        'stop_code': stop_code,
                        'time': time,
                        'branch_code': branch_code,
                        'platform': platform,
                        'countdown': countdown
                    }

                    is_first_departure = False

                    departures_list.append(departure_item)

    departures_list.sort(key=lambda x: x['countdown'])

    return jsonify(departures_list)
            

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode