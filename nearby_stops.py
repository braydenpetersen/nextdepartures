import requests
import math
from datetime import datetime
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# Load environment variables from .env file
load_dotenv()

API_KEY = os.environ.get("API_KEY")
MAX_DISTANCE = os.environ.get("RADIUS")

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="Geopy Library")
# entering the location name
getLoc = loc.geocode(input("Enter location: "))
# printing address
print(getLoc.address)

LAT = getLoc.latitude
LON = getLoc.longitude

currentTime = datetime.now().timestamp()
localTime = datetime.now()

print(f"\nDepartures for {localTime}")

payload = {
    'lat' : LAT,
    'lon' : LON,
    'max_distance' : MAX_DISTANCE
}

header = {"apiKey" : API_KEY}


nearby_stops = requests.get(
    "https://external.transitapp.com/v3/public/nearby_stops", params=payload, headers=header
)


for x in nearby_stops.json()['stops']:
    stopId = [x][0]['global_stop_id']
    stopName = [x][0]['stop_name']
    stopCode = [x][0]['stop_code']

    stopInfo = {
        'global_stop_id' : stopId
    }

    departures = requests.get(
        "https://external.transitapp.com/v3/public/stop_departures", params=stopInfo, headers=header
    )

    print("\n" + stopName + " [" + stopCode + "] " + stopId)
    for i in range(3):
        headsign = departures.json()['route_departures'][0]['itineraries'][0]['headsign'] # destination
        route_short_name = departures.json()['route_departures'][0]['route_short_name'] # route name or number

        # add extra detail if iON
        if route_short_name == "301":
            route_short_name = "301 iON"

        currentDeparture = math.floor((departures.json()['route_departures'][0]['itineraries'][0]['schedule_items'][i]['departure_time']) - currentTime)
        
        timeUnit = "min"

        if currentDeparture > 60:
            currentDeparture = math.floor(currentDeparture/60)
        else:
            timeUnit ="s"

        print(f"{route_short_name} to {headsign}\t\t{currentDeparture} {timeUnit}")

    print("\n=========================================================")