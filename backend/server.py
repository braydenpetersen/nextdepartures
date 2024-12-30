import csv
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
API_KEY = os.getenv('METROLINX_API_KEY')
STOP_CODE = os.getenv('STOP_CODE')

def get_GOtransit_data():
    payload = {
        'StopCode': STOP_CODE,
        'key': API_KEY
    }
    # get the data from the API
    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    data = response.json()

    extracted_data = []
    for line in data.get('NextService', {}).get('Lines', []):
        routeNumber = line.get('LineCode', '').strip()
        direction_name = line.get('DirectionName', '')
        headsign = direction_name.split('-', 1)[1].strip() if '-' in direction_name else ''
        
        # Extract branchCode from non-numerical values before the dash in DirectionName
        branchCode = ''.join(filter(lambda x: not x.isdigit(), direction_name.split('-', 1)[0])).strip()

        # Convert ComputedDepartureTime to UNIX timestamp
        departure_time_str = line.get('ComputedDepartureTime')
        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d %H:%M:%S')
        time = departure_time.strftime('%H:%M')
        departure_time_unix = int(departure_time.timestamp())
        
        # Compute countdown in minutes
        current_time_unix = int(datetime.now().timestamp())
        countdown = (departure_time_unix - current_time_unix) // 60
        if countdown < 0:
            continue # Skip if the trip has already left

        routeColor, routeTextColor = get_route_colors(routeNumber)

        extracted_data.append({
            'stop_code': line.get('StopCode'),
            'routeNumber': routeNumber,
            'headsign': headsign,
            'platform': line.get('ScheduledPlatform'),
            'routeNetwork': 'GO',
            'time': time,
            'countdown': countdown,
            'branchCode': branchCode,
            'routeColor': routeColor,
            'routeTextColor': routeTextColor
        })
    return extracted_data

def get_route_colors(route_number):
    with open('GO-GTFS/routes.txt', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['route_short_name'] == str(route_number):
                return row['route_color'], row['route_text_color']
    return None, None

''''

def get_GRT_data():
    url = "https://grtivr-prod.regionofwaterloo.9802690.ca/vms/graphql"
    query = """
    query GetFilteredStopsAndDepartures {
      stops(filter: {idIn: ["6004", "6120", "1260", "1262", "1223", "1264", "1078"]}) {
        id
        platformCode
        arrivals(limit: 5) {
          trip {
            headsign
          }
          route {
            shortName
            longName
          }
          departure
        }
      }
    }
    """
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}"}


def load_stop_code_mapping():
    with open('static/stop_code_to_platform.json', 'r') as f:
        return json.load(f)

def remove_station(headsign):
    return headsign.replace("Station", "").strip()

'''

# api/test
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Hello from the server!',
    })

# api/departures
@app.route('/api/departures', methods=['GET'])
def get_departures():

    departures_list = []

    departures_list.sort(key=lambda x: x['countdown'])

    return jsonify(departures_list)
            

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode