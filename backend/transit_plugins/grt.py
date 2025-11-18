import csv
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Tuple, Optional
from .base_plugin import TransitPlugin, Departure

class GRTPlugin(TransitPlugin):
    """Grand River Transit plugin for fetching real-time departures"""
    
    @property
    def network_name(self) -> str:
        return "GRT"
    
    @property
    def requires_api_key(self) -> bool:
        return False
    
    def get_departures(self, stop_ids: List[str]) -> List[Departure]:
        """Fetch GRT departures for given stop IDs (supports batch requests)"""
        if not stop_ids:
            return []
        
        # Convert stop IDs to strings and format for GraphQL
        formatted_stop_ids = [f'"{str(stop_id)}"' for stop_id in stop_ids]
        stop_ids_str = ", ".join(formatted_stop_ids)
        
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
        
        try:
            response = requests.post(url, json={"query": query}, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching GRT departures: {e}")
            return []
        
        extracted_data = []
        est_tz = ZoneInfo('America/New_York')

        for stop in data.get('data', {}).get('stops', []):
            for arrival in stop.get('arrivals', []):
                trip = arrival.get('trip', {})
                route = arrival.get('route', {})

                route_number = route.get('shortName', '')
                headsign = trip.get('headsign', '') or route.get('longName', '')
                
                if '-' in headsign:
                    parts = headsign.split('-', 1)
                    before_dash = parts[0].strip()
                    # Only extract branch code if it's a single letter before the dash
                    if len(before_dash) == 1 and before_dash.isalpha():
                        branch_code = before_dash
                        headsign = parts[1].strip()
                    else:
                        branch_code = ''
                else:
                    branch_code = ''

                # Convert departure time to UNIX timestamp
                departure_time_str = arrival.get('departure')
                if not departure_time_str:
                    continue
                    
                try:
                    departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M:%S%z')
                    departure_time = departure_time.astimezone(est_tz)
                    time = departure_time.strftime('%H:%M')
                    departure_time_unix = int(departure_time.timestamp())

                    # Compute countdown in minutes
                    current_time_est = datetime.now(est_tz)
                    current_time_unix = int(current_time_est.timestamp())
                    countdown = (departure_time_unix - current_time_unix) // 60

                    if countdown < -1:
                        continue  # Skip if the trip has already left
                except Exception as e:
                    print(f"Error parsing GRT departure time {departure_time_str}: {e}")
                    continue
                
                route_color, route_text_color = self.get_route_colors(route_number)

                extracted_data.append(Departure(
                    stop_id=stop.get('id'),
                    route_number=route_number,
                    headsign=headsign,
                    platform=stop.get('platformCode'),
                    route_network='GRT',
                    time=time,
                    countdown=countdown,
                    branch_code=branch_code,
                    route_color=route_color,
                    route_text_color=route_text_color
                ))
                
        return extracted_data
    
    def get_route_colors(self, route_number: str) -> Tuple[Optional[str], Optional[str]]:
        """Get route colors from GTFS data"""
        file_path = 'data/GTFS/GRT_GTFS/routes.txt'
        
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if row['route_short_name'] == str(route_number):
                        route_color = f"#{row['route_color']}" if row.get('route_color') else None
                        route_text_color = f"#{row['route_text_color']}" if row.get('route_text_color') else None
                        return route_color, route_text_color
        except Exception as e:
            print(f"Error reading GRT routes file: {e}")
        
        return None, None