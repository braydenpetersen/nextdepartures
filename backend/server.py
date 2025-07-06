import csv
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from dotenv import load_dotenv
from functools import wraps


# get the environment variables
load_dotenv()
API_KEY = os.environ.get('API_KEY')
GO_API_KEY = os.environ.get('GO_API_KEY')

# app instance
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://transit.braydenpetersen.com"])

def requires_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if API_KEY is properly loaded
        if not API_KEY:
            print("ERROR: API_KEY environment variable not set!")
            return jsonify({'error': 'Server configuration error'}), 500
            
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_GOtransit_departures(STOP_CODE):
    payload = {
        'StopCode': STOP_CODE,
        'key': GO_API_KEY
    }

    # get the data from the API
    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    data = response.json()

    est_tz = ZoneInfo('America/New_York')

    extracted_data = []
    next_service = data.get('NextService', {})
    if not next_service:
        return extracted_data

    for line in next_service.get('Lines', []):
        routeNumber = line.get('LineCode', '').strip()
        direction_name = line.get('DirectionName', '')
        headsign = direction_name.split('-', 1)[1].strip() if '-' in direction_name else ''
        
        if any(char.isdigit() for char in direction_name):
            # Extract branchCode from non-numerical values before the dash in DirectionName
            branchCode = ''.join(filter(lambda x: not x.isdigit(), direction_name.split('-', 1)[0])).strip()
        else:
            branchCode = ''


        # Convert ComputedDepartureTime to UNIX timestamp
        departure_time_str = line.get('ComputedDepartureTime')
        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d %H:%M:%S')
        departure_time = departure_time.replace(tzinfo=est_tz)
        time = departure_time.strftime('%H:%M')
        departure_time_unix = int(departure_time.timestamp())
        
        # Compute countdown in minutes
        current_time_est = datetime.now(est_tz)
        current_time_unix = int(current_time_est.timestamp())
        countdown = (departure_time_unix - current_time_unix) // 60

        if countdown < -1:
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

    est_tz = ZoneInfo('America/New_York')

    for stop in response.json().get('data', {}).get('stops', []):
      for arrival in stop.get('arrivals', []):
        trip = arrival.get('trip', {})
        route = arrival.get('route', {})

        routeNumber = route.get('shortName', '')
        headsign = trip.get('headsign', '') or route.get('longName', '')
        
        if '-' in headsign:
            parts = headsign.split('-', 1)
            before_dash = parts[0].strip()
            # Only extract branch code if it's a single letter before the dash
            if len(before_dash) == 1 and before_dash.isalpha():
                branchCode = before_dash
                headsign = parts[1].strip()
            else:
                branchCode = ''
        else:
            branchCode = ''

        # Convert departure time to UNIX timestamp
        departure_time_str = arrival.get('departure')
        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M:%S%z')

        # Convert to EST
        
        departure_time = departure_time.astimezone(est_tz)
       
        
        time = departure_time.strftime('%H:%M')
        departure_time_unix = int(departure_time.timestamp())

        # Compute countdown in minutes
        current_time_est = datetime.now(est_tz)
        current_time_unix = int(current_time_est.timestamp())
        countdown = (departure_time_unix - current_time_unix) // 60
        if countdown < -1:
            continue # Skip if the trip has already left
        
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

def test_metrolinx_api(STOP_CODE):
    payload = {
        'StopCode': STOP_CODE,
        'key': GO_API_KEY
    }

    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    return response.json()

# api/departures
@app.route('/api/departures', methods=['GET'])
@requires_api_key
def get_departures():
    STOP_CODE = request.args.get('stopCode', '02799')

    print(STOP_CODE)

    departures_list = []

    # grt_data = get_GRT_data()

    departures_list.extend(get_GOtransit_departures(STOP_CODE))
    if STOP_CODE == '02799':
        departures_list.extend(get_GRT_departures())

    # First group by network
    network_groups = {}
    for departure in departures_list:
        network = departure['routeNetwork']
        if network not in network_groups:
            network_groups[network] = {
                'network': network,
                'routes': {}
            }
        
        # Create a key that includes all grouping criteria for routes
        route_key = f"{departure['routeNumber']}-{departure['headsign']}-{departure['branchCode']}"
        if route_key not in network_groups[network]['routes']:
            network_groups[network]['routes'][route_key] = {
                'routeNetwork': departure['routeNetwork'],
                'routeNumber': departure['routeNumber'],
                'headsign': departure['headsign'],
                'branchCode': departure['branchCode'],
                'platform': departure['platform'],
                'routeColor': departure['routeColor'],
                'routeTextColor': departure['routeTextColor'],
                'stopCode': departure['stopCode'],
                'departures': []
            }
        
        # Add the time and countdown to the departures list
        time = "Now" if departure['countdown'] <= 1 else departure['time']
        network_groups[network]['routes'][route_key]['departures'].append({
            'time': time,
            'countdown': departure['countdown']
        })

    # Sort departures within each route group by countdown
    for network in network_groups.values():
        for route in network['routes'].values():
            route['departures'].sort(key=lambda x: x['countdown'])
            # Only keep the first two departures
            route['departures'] = route['departures'][:2]

    # Convert to list and sort networks by the first departure's countdown
    result = []
    for network in network_groups.values():
        routes_list = list(network['routes'].values())
        routes_list.sort(key=lambda x: x['departures'][0]['countdown'] if x['departures'] else float('inf'))
        network['routes'] = routes_list
        result.append(network)

    # Sort networks alphabetically
    result.sort(key=lambda x: x['network'])

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode