import csv
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from functools import wraps
from difflib import SequenceMatcher


# get the environment variables
load_dotenv()
API_KEY = os.environ.get('API_KEY')
GO_API_KEY = os.environ.get('GO_API_KEY')

# app instance
app = Flask(__name__)
CORS(app, methods=["GET"], allow_headers=["X-API-Key", "Content-Type"])

def requires_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def map_go_route_number(route_number):
    """Map GO Transit route numbers to their correct identifiers."""
    mapping = {
        'GT': 'KI'  # Georgetown -> Kitchener
    }
    return mapping.get(route_number, route_number)

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
        # Map the route number to correct identifier
        routeNumber = map_go_route_number(routeNumber)
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
    file_path = 'data/GTFS/GO-GTFS/routes.txt' if route_network == 'GO' else 'data/GTFS/GRT_GTFS/routes.txt'
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # For GO routes, match either the route_short_name or the route ID suffix
            if route_network == 'GO':
                # Check if route_id exists in the row before trying to use it
                route_id_match = 'route_id' in row and row['route_id'].endswith(f'-{route_number}')
                if row['route_short_name'] == str(route_number) or route_id_match:
                    route_color = f"#{row['route_color']}"
                    route_text_color = f"#{row['route_text_color']}"
                    return route_color, route_text_color
            # For GRT routes, match only the route_short_name
            elif route_network == 'GRT' and row['route_short_name'] == str(route_number):
                route_color = f"#{row['route_color']}"
                route_text_color = f"#{row['route_text_color']}"
                return route_color, route_text_color
    return None, None

def get_GRT_departures(stop_codes=None):
    if stop_codes is None:
        stop_codes = ["6004", "6120", "1260", "1262", "1223", "1264", "1078"]  # Default to UW stops
    
    # Convert stop codes to strings and format for GraphQL
    stop_ids = [f'"{str(code)}"' for code in stop_codes]
    stop_ids_str = ", ".join(stop_ids)
    
    url = "https://grtivr-prod.regionofwaterloo.9802690.ca/vms/graphql"
    query = f"""
    query GetFilteredStopsAndDepartures {{
      stops(filter: {{idIn: [{stop_ids_str}]}}) {{
        id
        platformCode
        arrivals {{
          trip {{
            headsign
          }}
          route {{
            shortName
            longName
          }}
          departure
        }}
      }}
    }}
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


def test_metrolinx_api(STOP_CODE):
    payload = {
        'StopCode': STOP_CODE,
        'key': GO_API_KEY
    }

    response = requests.get('https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', params=payload)
    return response.json()

# test endpoint to check if the decorator is working
@app.route('/api/test', methods=['GET'])
@requires_api_key
def test_endpoint():
    return jsonify({'message': 'This should be protected'})

# api/departures
@app.route('/api/departures', methods=['GET'])
@requires_api_key
def get_departures():
    # Get comma-separated stops with agency prefixes: GRT_1078,GO_02799,GO_02800
    stops_param = request.args.get('stops', '')
    
    if not stops_param:
        return jsonify({'error': 'stops parameter is required (e.g., ?stops=GRT_1078,GO_02799)'}), 400
    
    departures_list = []
    stop_codes = [stop.strip() for stop in stops_param.split(',') if stop.strip()]
    
    # Collect GRT stop codes to batch the request
    grt_codes = []
    
    for stop_code in stop_codes:
        if '_' not in stop_code:
            continue
            
        agency, code = stop_code.split('_', 1)
        
        try:
            if agency.upper() == 'GO':
                departures_list.extend(get_GOtransit_departures(code))
            elif agency.upper() == 'GRT':
                grt_codes.append(code)
            else:
                continue
        except Exception as e:
            print(f"Error getting departures for {stop_code}: {e}")
            continue
    
    # Get GRT departures for all GRT stops in one request
    if grt_codes:
        try:
            departures_list.extend(get_GRT_departures(grt_codes))
        except Exception as e:
            print(f"Error getting GRT departures: {e}")

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

def load_consolidated_stations():
    """Load the consolidated stations from JSON file."""
    try:
        with open('static/consolidated_stations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def station_name_similarity(query: str, station_name: str) -> float:
    """Calculate similarity between search query and station name."""
    query_lower = query.lower().strip()
    station_lower = station_name.lower().strip()
    
    # Exact match
    if query_lower == station_lower:
        return 1.0
    
    # Check if query matches the start of station name (high priority)
    if station_lower.startswith(query_lower):
        return 0.95
    
    # Check if query is contained in station name
    if query_lower in station_lower:
        return 0.9
    
    # Check if any word in station name starts with query
    station_words = station_lower.split()
    for word in station_words:
        if word.startswith(query_lower):
            return 0.85
    
    # Fuzzy matching
    return SequenceMatcher(None, query_lower, station_lower).ratio()

@app.route('/api/stations/search', methods=['GET'])
@requires_api_key
def search_stations():
    """
    Search for stations by name.
    Query params:
    - q: search query (required)
    - agencies: comma-separated list of agencies to filter (optional)
    - limit: max number of results (default: 10)
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query (q) is required'}), 400
    
    agencies_param = request.args.get('agencies', '')
    wanted_agencies = set()
    if agencies_param:
        wanted_agencies = set(agency.strip().upper() for agency in agencies_param.split(','))
    
    limit = int(request.args.get('limit', 10))
    
    # Load consolidated stations
    stations = load_consolidated_stations()
    
    # Filter and score stations
    scored_stations = []
    for station in stations:
        # Calculate similarity score
        score = station_name_similarity(query, station['station_name'])
        
        # Skip if score is too low
        if score < 0.3:
            continue
        
        # Filter by agencies if specified
        if wanted_agencies:
            station_agencies = set(stop['agency'] for stop in station['stops'])
            if not station_agencies.intersection(wanted_agencies):
                continue
        
        # Filter stops by agencies if specified
        filtered_stops = station['stops']
        if wanted_agencies:
            filtered_stops = [stop for stop in station['stops'] if stop['agency'] in wanted_agencies]
        
        # Add a small bonus for stations with more stops (major hubs)
        stop_count_bonus = min(len(filtered_stops) * 0.05, 0.2)  # Max 0.2 bonus
        final_score = score + stop_count_bonus
        
        scored_stations.append({
            'station_id': station['station_id'],
            'station_name': station['station_name'], 
            'station_lat': station['station_lat'],
            'station_lon': station['station_lon'],
            'stops': filtered_stops,
            'score': final_score
        })
    
    # Sort by score (descending) and limit results
    scored_stations.sort(key=lambda x: x['score'], reverse=True)
    results = scored_stations[:limit]
    
    # Remove score from final results
    for result in results:
        del result['score']
    
    return jsonify({
        'query': query,
        'total_results': len(results),
        'stations': results
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode