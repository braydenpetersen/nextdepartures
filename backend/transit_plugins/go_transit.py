import csv
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Tuple, Optional
from .base_plugin import TransitPlugin, Departure

class GOTransitPlugin(TransitPlugin):
    """GO Transit plugin for fetching real-time departures"""
    
    @property
    def network_name(self) -> str:
        return "GO"
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = config.get('api_key') if config else None
        if not self.api_key:
            raise ValueError("GO Transit plugin requires an API key")
    
    def map_route_number(self, route_number: str) -> str:
        """Map GO Transit route numbers to their correct identifiers."""
        mapping = {
            'GT': 'KI'  # Georgetown -> Kitchener
        }
        return mapping.get(route_number, route_number)
    
    def get_departures(self, stop_id: str) -> List[Departure]:
        """Fetch GO Transit departures for a given stop ID"""
        payload = {
            'StopCode': stop_id,
            'key': self.api_key
        }

        try:
            response = requests.get(
                'https://api.openmetrolinx.com/OpenDataAPI/api/V1/Stop/NextService/', 
                params=payload
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching GO departures for {stop_id}: {e}")
            return []

        est_tz = ZoneInfo('America/New_York')
        extracted_data = []
        
        next_service = data.get('NextService', {})
        if not next_service:
            return extracted_data

        for line in next_service.get('Lines', []):
            route_number = line.get('LineCode', '').strip()
            route_number = self.map_route_number(route_number)
            direction_name = line.get('DirectionName', '')
            headsign = direction_name.split('-', 1)[1].strip() if '-' in direction_name else ''
            
            if any(char.isdigit() for char in direction_name):
                branch_code = ''.join(filter(lambda x: not x.isdigit(), direction_name.split('-', 1)[0])).strip()
            else:
                branch_code = ''

            # Convert ComputedDepartureTime to UNIX timestamp
            departure_time_str = line.get('ComputedDepartureTime')
            if not departure_time_str:
                continue
                
            try:
                departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d %H:%M:%S')
                departure_time = departure_time.replace(tzinfo=est_tz)
                time = departure_time.strftime('%H:%M')
                departure_time_unix = int(departure_time.timestamp())
                
                # Compute countdown in minutes
                current_time_est = datetime.now(est_tz)
                current_time_unix = int(current_time_est.timestamp())
                countdown = (departure_time_unix - current_time_unix) // 60

                if countdown < -1:
                    continue  # Skip if the trip has already left

                if countdown < 10:
                    time = f"{int(countdown)} min"
            except Exception as e:
                print(f"Error parsing departure time {departure_time_str}: {e}")
                continue

            route_color, route_text_color = self.get_route_colors(route_number)

            extracted_data.append(Departure(
                stop_id=line.get('StopCode'),
                route_number=route_number,
                headsign=headsign,
                platform=line.get('ScheduledPlatform'),
                route_network='GO',
                time=time,
                countdown=countdown,
                branch_code=branch_code,
                route_color=route_color,
                route_text_color=route_text_color
            ))

        return extracted_data
    
    def get_route_colors(self, route_number: str) -> Tuple[Optional[str], Optional[str]]:
        """Get route colors from GTFS data"""
        file_path = 'data/GTFS/GO-GTFS/routes.txt'
        
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Check if route_id exists in the row before trying to use it
                    route_id_match = 'route_id' in row and row['route_id'].endswith(f'-{route_number}')
                    if row['route_short_name'] == str(route_number) or route_id_match:
                        route_color = f"#{row['route_color']}" if row.get('route_color') else None
                        route_text_color = f"#{row['route_text_color']}" if row.get('route_text_color') else None
                        return route_color, route_text_color
        except Exception as e:
            print(f"Error reading GO routes file: {e}")
        
        return None, None