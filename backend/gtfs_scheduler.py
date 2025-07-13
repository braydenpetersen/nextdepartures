"""
GTFS Static Schedule Integration

FIXME: This module is currently duplicating departures instead of properly 
deduplicating them. Needs debugging of the merge logic and departure key 
matching before re-enabling.

Always integrates GTFS static schedule data with real-time departures to provide
a complete departure schedule. Handles deduplication and time windowing.
"""

import csv
import os
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Set
import pytz


class GTFSScheduler:
    def __init__(self, gtfs_data_dir: str = 'data/GTFS'):
        self.gtfs_data_dir = gtfs_data_dir
        self.toronto_tz = pytz.timezone('America/Toronto')
        
        # Look-ahead window for static schedules (in hours)
        self.SCHEDULE_LOOKAHEAD_HOURS = 3
        
        # Cache for GTFS data to avoid repeated file reads
        self._routes_cache = {}
        self._trips_cache = {}
        self._calendar_dates_cache = {}
        
    def _load_routes(self, agency: str) -> Dict:
        """Load and cache routes for an agency."""
        if agency in self._routes_cache:
            return self._routes_cache[agency]
            
        routes = {}
        gtfs_dir = f'{agency}_GTFS' if agency == 'GRT' else f'{agency}-GTFS'
        routes_file = os.path.join(self.gtfs_data_dir, gtfs_dir, 'routes.txt')
        
        if not os.path.exists(routes_file):
            self._routes_cache[agency] = routes
            return routes
            
        try:
            with open(routes_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    routes[row['route_id']] = {
                        'route_short_name': row.get('route_short_name', ''),
                        'route_long_name': row.get('route_long_name', ''),
                        'route_color': row.get('route_color', ''),
                        'route_text_color': row.get('route_text_color', ''),
                    }
        except Exception as e:
            print(f"Error loading routes for {agency}: {e}")
            
        self._routes_cache[agency] = routes
        return routes
    
    def _load_trips(self, agency: str) -> Dict:
        """Load and cache trips for an agency."""
        if agency in self._trips_cache:
            return self._trips_cache[agency]
            
        trips = {}
        gtfs_dir = f'{agency}_GTFS' if agency == 'GRT' else f'{agency}-GTFS'
        trips_file = os.path.join(self.gtfs_data_dir, gtfs_dir, 'trips.txt')
        
        if not os.path.exists(trips_file):
            self._trips_cache[agency] = trips
            return trips
            
        try:
            with open(trips_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trips[row['trip_id']] = {
                        'route_id': row.get('route_id', ''),
                        'service_id': row.get('service_id', ''),
                        'trip_headsign': row.get('trip_headsign', ''),
                        'direction_id': row.get('direction_id', ''),
                    }
        except Exception as e:
            print(f"Error loading trips for {agency}: {e}")
            
        self._trips_cache[agency] = trips
        return trips
    
    def _load_calendar_dates(self, agency: str) -> Dict:
        """Load and cache calendar dates for an agency."""
        if agency in self._calendar_dates_cache:
            return self._calendar_dates_cache[agency]
            
        calendar_dates = {}
        gtfs_dir = f'{agency}_GTFS' if agency == 'GRT' else f'{agency}-GTFS'
        calendar_file = os.path.join(self.gtfs_data_dir, gtfs_dir, 'calendar_dates.txt')
        
        if not os.path.exists(calendar_file):
            self._calendar_dates_cache[agency] = calendar_dates
            return calendar_dates
            
        try:
            with open(calendar_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    service_id = row['service_id']
                    date_str = row['date']
                    exception_type = int(row['exception_type'])
                    
                    if service_id not in calendar_dates:
                        calendar_dates[service_id] = {}
                    calendar_dates[service_id][date_str] = exception_type
        except Exception as e:
            print(f"Error loading calendar dates for {agency}: {e}")
            
        self._calendar_dates_cache[agency] = calendar_dates
        return calendar_dates
    
    def _is_service_active(self, agency: str, service_id: str, date_str: str) -> bool:
        """Check if a service is active on a given date."""
        calendar_dates = self._load_calendar_dates(agency)
        
        if service_id in calendar_dates and date_str in calendar_dates[service_id]:
            # exception_type: 1 = service added, 2 = service removed
            return calendar_dates[service_id][date_str] == 1
        
        return False
    
    def _parse_gtfs_time(self, time_str: str) -> Optional[time]:
        """Parse GTFS time format (HH:MM:SS) which can exceed 24 hours."""
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            
            # Handle times >= 24:00:00 (next day service)
            if hours >= 24:
                hours = hours % 24
                
            return time(hours, minutes, seconds)
        except (ValueError, IndexError):
            return None
    
    def _create_departure_key(self, departure: Dict) -> str:
        """Create a unique key for departure deduplication."""
        # Use route, headsign, and rounded time for matching
        # Handle both real-time format (routeNumber) and static format (route_number)
        route = departure.get('routeNumber', departure.get('route_number', ''))
        headsign = departure.get('headsign', '').lower().strip()
        time_str = departure.get('time', '')
        
        return f"{route}|{headsign}|{time_str}"
    
    def get_static_departures(self, stop_ids: List[str]) -> List[Dict]:
        """
        Get static schedule departures for given stop IDs within the lookahead window.
        
        Args:
            stop_ids: List of stop IDs with agency prefix (e.g., ['GO_UN', 'GRT_1078'])
            
        Returns:
            List of departure dictionaries from static schedules
        """
        all_departures = []
        current_datetime = self.toronto_tz.localize(datetime.now())
        end_datetime = current_datetime + timedelta(hours=self.SCHEDULE_LOOKAHEAD_HOURS)
        current_date_str = current_datetime.strftime('%Y%m%d')
        
        for stop_id in stop_ids:
            try:
                # Parse agency and original stop ID
                if '_' not in stop_id:
                    continue
                    
                agency, original_stop_id = stop_id.split('_', 1)
                
                # Load necessary data
                routes = self._load_routes(agency)
                trips = self._load_trips(agency)
                
                # Load stop times
                gtfs_dir = f'{agency}_GTFS' if agency == 'GRT' else f'{agency}-GTFS'
                stop_times_file = os.path.join(self.gtfs_data_dir, gtfs_dir, 'stop_times.txt')
                
                if not os.path.exists(stop_times_file):
                    continue
                
                with open(stop_times_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        # Check if this is for our stop
                        if row['stop_id'] != original_stop_id:
                            continue
                        
                        trip_id = row['trip_id']
                        departure_time_str = row['departure_time']
                        
                        # Parse departure time
                        departure_time = self._parse_gtfs_time(departure_time_str)
                        if not departure_time:
                            continue
                        
                        # Get trip info
                        if trip_id not in trips:
                            continue
                        
                        trip_info = trips[trip_id]
                        service_id = trip_info['service_id']
                        
                        # Check if service is active today
                        if not self._is_service_active(agency, service_id, current_date_str):
                            continue
                        
                        # Create departure datetime
                        departure_datetime = datetime.combine(current_datetime.date(), departure_time)
                        departure_datetime = self.toronto_tz.localize(departure_datetime)
                        
                        # Check if departure is within our time window
                        if departure_datetime <= current_datetime or departure_datetime > end_datetime:
                            continue
                        
                        # Get route info
                        route_id = trip_info['route_id']
                        route_info = routes.get(route_id, {})
                        
                        # Calculate countdown
                        countdown_seconds = (departure_datetime - current_datetime).total_seconds()
                        countdown_minutes = max(1, int(countdown_seconds / 60))
                        
                        # Format time
                        formatted_time = departure_time.strftime('%H:%M')
                        
                        # Create departure object
                        departure = {
                            'stop_id': stop_id,
                            'route_number': route_info.get('route_short_name', route_id),
                            'headsign': trip_info.get('trip_headsign', ''),
                            'platform': '',
                            'route_network': agency,
                            'time': formatted_time,
                            'countdown': countdown_minutes,
                            'branch_code': '',
                            'route_color': route_info.get('route_color', ''),
                            'route_text_color': route_info.get('route_text_color', ''),
                            'is_static': True
                        }
                        
                        all_departures.append(departure)
                        
            except Exception as e:
                print(f"Error getting static departures for {stop_id}: {e}")
        
        # Sort by countdown
        all_departures.sort(key=lambda x: x['countdown'])
        return all_departures
    
    def merge_departures(self, realtime_departures: List[Dict], static_departures: List[Dict]) -> List[Dict]:
        """
        Merge real-time and static departures, removing duplicates and maintaining order.
        
        Args:
            realtime_departures: List of real-time departure objects
            static_departures: List of static schedule departure objects
            
        Returns:
            Merged and deduplicated list of departures
        """
        # Create sets of keys for deduplication
        realtime_keys = set()
        for departure in realtime_departures:
            key = self._create_departure_key(departure)
            realtime_keys.add(key)
        
        # Add static departures that don't duplicate real-time ones
        merged_departures = list(realtime_departures)
        
        for static_departure in static_departures:
            static_key = self._create_departure_key(static_departure)
            
            # Only add if not already covered by real-time data
            if static_key not in realtime_keys:
                merged_departures.append(static_departure)
        
        # Sort by countdown
        merged_departures.sort(key=lambda x: x.get('countdown', float('inf')))
        
        return merged_departures