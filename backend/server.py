import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import json


# app instance
app = Flask(__name__)
CORS(app)

# get the environment variables
API_KEY = os.environ.get('METROLINX_API_KEY')
STOP_CODE = "02799" # GO TRANSIT STOP CODE for University of Waterloo Station

def get_GOtransit_departures():
    payload = {
        'StopCode': STOP_CODE,
        'key': os.environ.get('METROLINX_API_KEY')
    }

    print(f"Payload: {payload}")

    # get the data from the API
    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    data = response.json()

    extracted_data = []
    next_service = data.get('NextService', {})
    if not next_service:
        return extracted_data
    for line in next_service.get('Lines', []):
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

        if countdown < 10:
            time = f"{int(countdown)} min"

        routeColor, routeTextColor = get_route_colors(routeNumber, "GO")

        extracted_data.append({
            'stopCode': line.get('StopCode'),
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

def get_route_colors(route_number, route_network):
    file_path = 'static/GO-GTFS/routes.txt' if route_network == 'GO' else 'static/GRT_GTFS/routes.txt'
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['route_short_name'] == str(route_number):
                route_color = f"#{row['route_color']}"
                route_text_color = f"#{row['route_text_color']}"
                return route_color, route_text_color
    return None, None

def get_GRT_departures():
    url = "https://grtivr-prod.regionofwaterloo.9802690.ca/vms/graphql"
    query = """
    query GetFilteredStopsAndDepartures {
      stops(filter: {idIn: ["6004", "6120", "1260", "1262", "1223", "1264", "1078"]}) {
        id
        platformCode
        arrivals {
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
    
    extracted_data = []

    for stop in response.json().get('data', {}).get('stops', []):
      for arrival in stop.get('arrivals', []):
        trip = arrival.get('trip', {})
        route = arrival.get('route', {})

        routeNumber = route.get('shortName', '')
        headsign = remove_station(trip.get('headsign', '') or route.get('longName', ''))
        
        if '-' in headsign:
            # Extract branchCode from non-numerical values before the dash in DirectionName
            branchCode = ''.join(filter(lambda x: not x.isdigit(), headsign.split('-', 1)[0])).strip()
            headsign = headsign.split('-', 1)[1].strip()
        else:
            branchCode = ''

        # Convert departure time to UNIX timestamp
        departure_time_str = arrival.get('departure')
        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M:%S%z')

        # Convert to EST
        est = ZoneInfo('America/New_York')
        departure_time = departure_time.astimezone(est)
       
        
        time = departure_time.strftime('%H:%M')
        departure_time_unix = int(departure_time.timestamp())

        # Compute countdown in minutes
        current_time_unix = int(datetime.now().timestamp())
        countdown = (departure_time_unix - current_time_unix) // 60
        if countdown < 0:
            continue # Skip if the trip has already left

        if countdown < 10:
            time = f"{int(countdown)} min"
        
        routeColor, routeTextColor = get_route_colors(routeNumber, "GRT")

        extracted_data.append({
          'stopCode': stop.get('id'),
          'routeNumber': routeNumber,
          'headsign': headsign,
          'platform': stop.get('platformCode'),
          'routeNetwork': 'GRT',
          'time': time,
          'countdown': countdown,  # Assuming countdown is not available in the response
          'branchCode': branchCode,  # Assuming branchCode is not available in the response
          'routeColor': routeColor,  # Assuming routeColor is not available in the response
          'routeTextColor': routeTextColor  # Assuming routeTextColor is not available in the response
        })
    return extracted_data


def load_stop_code_mapping():
    with open('static/stop_code_to_platform.json', 'r') as f:
        return json.load(f)

def remove_station(headsign):
    return headsign.replace("Station", "").strip()

# api/test
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Hello from the server!',
        'test': 'test'
    })

# api/departures
@app.route('/api/departures', methods=['GET'])
def get_departures():

    departures_list = []

    go_transit_data = get_GOtransit_departures()
    # grt_data = get_GRT_data()

    departures_list.extend(go_transit_data)
    departures_list.extend(get_GRT_departures())

    departures_list.sort(key=lambda x: x['countdown'])

    return jsonify(departures_list)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode