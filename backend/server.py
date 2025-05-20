import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from dotenv import load_dotenv
# get the environment variables
load_dotenv()
API_KEY = os.environ.get('API_KEY')

# app instance
app = Flask(__name__)
CORS(app)
app.config['API_KEY'] = os.getenv('API_KEY')

def get_GOtransit_departures(STOP_CODE):
    payload = {
        'StopCode': STOP_CODE,
        'key': API_KEY
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

    est_tz = ZoneInfo('America/New_York')

    for stop in response.json().get('data', {}).get('stops', []):
      for arrival in stop.get('arrivals', []):
        trip = arrival.get('trip', {})
        route = arrival.get('route', {})

        routeNumber = route.get('shortName', '')
        headsign = remove_station(trip.get('headsign', '') or route.get('longName', ''))
        
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
        if countdown < 0:
            continue # Skip if the trip has already left

        if countdown < 60:
            time = f"{int(countdown)}"
        
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

def test_metrolinx_api(STOP_CODE):
    payload = {
        'StopCode': STOP_CODE,
        'key': API_KEY
    }

    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    return response.json()

# api/test
@app.route('/api/test', methods=['GET'])
def test():
    return test_metrolinx_api()

# api/departures
@app.route('/api/departures', methods=['GET'])
def get_departures():
    STOP_CODE = request.args.get('stopCode', '02799')

    print(STOP_CODE)

    departures_list = []

    # grt_data = get_GRT_data()

    departures_list.extend(get_GOtransit_departures(STOP_CODE))
    if STOP_CODE == '02799':
        departures_list.extend(get_GRT_departures())

    # Group departures by route line
    grouped_departures = {}
    for departure in departures_list:
        # Create a key that includes all grouping criteria
        key = f"{departure['routeNetwork']}-{departure['routeNumber']}-{departure['headsign']}-{departure['branchCode']}"
        if key not in grouped_departures:
            grouped_departures[key] = {
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
        # Add only the time and countdown to the departures list
        grouped_departures[key]['departures'].append({
            'time': departure['time'],
            'countdown': departure['countdown']
        })

    # Sort departures within each group by countdown
    for group in grouped_departures.values():
        group['departures'].sort(key=lambda x: x['countdown'])

    # Convert to list and sort groups by the first departure's countdown
    result = list(grouped_departures.values())
    result.sort(key=lambda x: x['departures'][0]['countdown'] if x['departures'] else float('inf'))

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode