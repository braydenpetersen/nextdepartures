import requests
import math
from datetime import datetime
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import threading

# Load environment variables from .env file
load_dotenv()

API_KEY = os.environ.get("API_KEY")
MAX_DISTANCE = os.environ.get("RADIUS")

LAT = 43.4745038
LON = -80.5397079

payload = {
    'lat' : LAT,
    'lon' : LON,
    'max_distance' : MAX_DISTANCE
}

currentTime = datetime.now().timestamp()
localTime = datetime.now()

header = {"apiKey" : API_KEY}

nearby_routes = requests.get(
    "https://external.transitapp.com/v3/public/nearby_routes", params=payload, headers=header
)

# go through all nearby routes
for x in nearby_routes.json()['routes']:

    # route info
    globalRouteId = [x][0]['global_route_id'] # unique route id (ie. GRT:2039)
    routeNum = [x][0]['route_short_name'] # route number
    routeLongName = [x][0]['route_long_name'] # route name (ie. Waterloo / Mississauga)
    modeName = [x][0]['mode_name'] # bus, train, etc

    routeNetworkName = [x][0]['route_network_name'] # network name (ie. GRT)

    # colors
    routeColor = [x][0]['route_color'] # hex color for surface
    routeTextColor = [x][0]['route_text_color'] # hex color for text

    compactShortName = [x][0]['compact_display_short_name']['elements'][1]

    # print route number, mode and name
    print(f"[{routeNetworkName}] {routeNum} {routeLongName} ({globalRouteId})")

    # check size of itineraries
    numItineraries = len([x][0]['itineraries'])

    # open all itineraries
    for i in range(numItineraries):

        numDepartures = len([x][0]['itineraries'][i]['schedule_items'])

        # open all schedule items
        for n in range(numDepartures):
            headsign = [x][0]['itineraries'][i]['headsign']

            departureTimestamp = [x][0]['itineraries'][i]['schedule_items'][n]['departure_time']
            departureTime = datetime.fromtimestamp(departureTimestamp).strftime('%H:%M')
            departureTimeMin = math.floor((departureTimestamp - currentTime) / 60)
                       
            print(f"{headsign}   {departureTime}   ({departureTimeMin} min)")

    
    print("\n====================\n")