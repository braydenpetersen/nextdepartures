import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from functools import wraps
from difflib import SequenceMatcher
from transit_plugins import PluginManager
# from gtfs_scheduler import GTFSScheduler  # Disabled due to duplication issues
from og_generator import OGImageGenerator


# get the environment variables
load_dotenv()
API_KEY = os.environ.get('API_KEY')
GO_API_KEY = os.environ.get('GO_API_KEY')

# Initialize plugin manager and OG image generator
plugin_config = {
    'GO_API_KEY': GO_API_KEY
}
plugin_manager = PluginManager(plugin_config)
# gtfs_scheduler = GTFSScheduler()  # Disabled due to duplication issues
og_generator = OGImageGenerator()

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


# test endpoint to check if the decorator is working
@app.route('/api/test', methods=['GET'])
@requires_api_key
def test_endpoint():
    return jsonify({'message': 'This should be protected'})

# api/departures
@app.route('/api/departures', methods=['GET'])
@requires_api_key
def get_departures():
    # Accept stops parameter (primary) or station ID (legacy support)
    stops_param = request.args.get('stops', '')
    station_param = request.args.get('station', '')

    stop_ids = []

    if stops_param:
        # Primary method: direct stop IDs
        stop_ids = [stop.strip() for stop in stops_param.split(',') if stop.strip()]
    elif station_param:
        # Legacy support: station ID lookup
        stations = load_consolidated_stations()
        station = next((s for s in stations if s['station_id'] == station_param), None)

        if not station:
            return jsonify({'error': f'Station not found: {station_param}'}), 404

        # Extract all stop IDs from the station
        stop_ids = [stop['stop_id'] for stop in station['stops'] if stop.get('stop_id')]

        if not stop_ids:
            return jsonify({'error': f'No valid stops found for station: {station_param}'}), 400
    else:
        return jsonify({'error': 'stops parameter is required (e.g., ?stops=GRT_1078,GO_02799)'}), 400
    
    # Use plugin manager to get departures
    departures_list = plugin_manager.get_departures_for_stops(stop_ids)
    
    # TODO: Re-enable GTFS scheduler integration once duplication issues are fixed
    # static_departures_list = gtfs_scheduler.get_static_departures(stop_ids)
    # all_departures = gtfs_scheduler.merge_departures(realtime_departures_dicts, static_departures_list)
    
    # Convert plugin Departure objects to dictionaries for compatibility
    departures_dicts = []
    for departure in departures_list:
        departures_dicts.append({
            'stopId': departure.stop_id,
            'routeNumber': departure.route_number,
            'headsign': departure.headsign,
            'platform': departure.platform,
            'routeNetwork': departure.route_network,
            'time': departure.time,
            'countdown': departure.countdown,
            'branchCode': departure.branch_code,
            'routeColor': departure.route_color,
            'routeTextColor': departure.route_text_color
        })

    # Group by network (existing grouping logic)
    network_groups = {}
    for departure in departures_dicts:
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
                'stopId': departure['stopId'],
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
            # Filter out any departures that left more than 1 minute ago (safety check)
            route['departures'] = [d for d in route['departures'] if d['countdown'] >= -1]
            route['departures'].sort(key=lambda x: x['countdown'])
            # Only keep the first two departures
            route['departures'] = route['departures'][:2]

    # Convert to list and sort networks by the first departure's countdown
    result = []
    for network in network_groups.values():
        routes_list = list(network['routes'].values())
        # Filter out routes with no departures
        routes_list = [route for route in routes_list if route['departures']]
        routes_list.sort(key=lambda x: x['departures'][0]['countdown'] if x['departures'] else float('inf'))
        network['routes'] = routes_list
        # Only add network if it has routes with departures
        if routes_list:
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

def station_name_similarity(query: str, station_name: str, stop_count: int = 1) -> float:
    """Calculate similarity between search query and station name."""
    query_lower = query.lower().strip()
    station_lower = station_name.lower().strip()
    is_major_hub = stop_count >= 2
    
    # Exact match
    if query_lower == station_lower:
        return 1.0
    
    # Check if query matches the start of station name (high priority)
    if station_lower.startswith(query_lower):
        # Major hubs get extra priority when query matches beginning
        if is_major_hub:
            return 0.98  # Higher than regular prefix match
        return 0.95
    
    # Check if query is contained in station name
    if query_lower in station_lower:
        return 0.9
    
    # Check if any word in station name starts with query
    station_words = station_lower.split()
    for word in station_words:
        if word.startswith(query_lower):
            # Major hubs get boost for word prefix matches too
            if is_major_hub:
                return 0.88
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
        # Filter by agencies if specified
        if wanted_agencies:
            station_agencies = set(stop['agency'] for stop in station['stops'])
            if not station_agencies.intersection(wanted_agencies):
                continue
        
        # Filter stops by agencies if specified
        filtered_stops = station['stops']
        if wanted_agencies:
            filtered_stops = [stop for stop in station['stops'] if stop['agency'] in wanted_agencies]
        
        # Calculate similarity score with stop count for major hub prioritization
        score = station_name_similarity(query, station['station_name'], len(filtered_stops))
        
        # Skip if score is too low
        if score < 0.3:
            continue
        
        # Add a small bonus for stations with more stops (major hubs)
        stop_count_bonus = min(len(filtered_stops) * 0.05, 0.2)  # Max 0.2 bonus
        
        # Give priority to GO Transit stations (regional transit)
        go_bonus = 0.0
        station_agencies = set(stop['agency'] for stop in filtered_stops)
        if 'GO' in station_agencies:
            go_bonus = 0.25  # Significant boost for GO stations
        
        # Check if user mentioned specific agency in search query (as standalone words)
        agency_query_bonus = 0.0
        query_words = set(query.lower().split())
        
        # Map agency mentions to actual agency codes (exact word matches only)
        agency_mentions = {
            'go': 'GO',
            'grt': 'GRT',
            'ion': 'GRT'  # ION is part of GRT
        }
        
        # Check for multi-word agency names
        query_lower = query.lower()
        if 'go transit' in query_lower and 'GO' in station_agencies:
            agency_query_bonus = 0.3
        elif 'grand river transit' in query_lower and 'GRT' in station_agencies:
            agency_query_bonus = 0.3
        elif 'grand river' in query_lower and 'GRT' in station_agencies:
            agency_query_bonus = 0.3
        else:
            # Check single word mentions
            for mention, agency_code in agency_mentions.items():
                if mention in query_words and agency_code in station_agencies:
                    agency_query_bonus = 0.3  # Higher than GO bonus to respect user intent
                    break
        
        final_score = score + stop_count_bonus + go_bonus + agency_query_bonus
        
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

@app.route('/api/og-image', methods=['GET'])
def generate_og_image():
    """
    Generate OpenGraph image for a station.
    Query params:
    - stops: comma-separated stop IDs to generate image for (optional)
    - name: station name to display (optional, will lookup from stops if not provided)
    - station: (legacy) station ID to generate image for (optional)
    """
    stops_param = request.args.get('stops', '')
    station_id = request.args.get('station', '')
    station_name = request.args.get('name', '')

    # If stops provided, look up the station name
    if stops_param and not station_name:
        stop_ids = [stop.strip() for stop in stops_param.split(',') if stop.strip()]
        if stop_ids:
            stations = load_consolidated_stations()
            # Find station that contains these stops
            for station in stations:
                station_stop_ids = [stop['stop_id'] for stop in station['stops']]
                if all(stop_id in station_stop_ids for stop_id in stop_ids):
                    station_name = station['station_name']
                    break

    # Legacy: If station ID provided, look up the station name
    elif station_id and not station_name:
        stations = load_consolidated_stations()
        station = next((s for s in stations if s['station_id'] == station_id), None)
        if station:
            station_name = station['station_name']
        else:
            return jsonify({'error': f'Station not found: {station_id}'}), 404

    # Generate image
    try:
        if station_name:
            image_bytes = og_generator.generate_station_image(station_name)
        else:
            # Default image for homepage
            image_bytes = og_generator.generate_default_image()

        # Return image with proper headers
        response = app.response_class(
            image_bytes,
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Content-Type': 'image/png'
            }
        )
        return response

    except Exception as e:
        print(f"Error generating OG image: {e}")
        return jsonify({'error': 'Failed to generate image'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0") # run the server in debug mode