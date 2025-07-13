#!/usr/bin/env python3
"""
Station Consolidation Script

Automatically discovers all GTFS feeds in data/ directory
and groups transit stops based on:
1. Geographic proximity (within 100 meters)
2. Name similarity (fuzzy matching)

Creates consolidated station records for unified departure board display.
"""

import csv
import json
import math
import os
import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in meters."""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def normalize_stop_name(name: str) -> str:
    """Normalize stop name for comparison."""
    # Remove common suffixes/prefixes and standardize
    name = name.lower().strip()
    
    # Remove common transit-related terms (order matters!)
    replacements = {
        ' go bus': '',
        ' go station': '',
        ' bus terminal': '',
        ' terminal': '',
        ' station': '',
        ' go': '',
        ' @ ': ' / ',
        'university of waterloo': 'uwaterloo',
        'university of': 'u',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name

def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two stop names (0-1)."""
    norm1 = normalize_stop_name(name1)
    norm2 = normalize_stop_name(name2)
    
    # Direct match after normalization
    if norm1 == norm2:
        return 1.0
    
    # Check if one is contained in the other
    if norm1 in norm2 or norm2 in norm1:
        return 0.9
    
    # Fuzzy string matching
    return SequenceMatcher(None, norm1, norm2).ratio()

def discover_gtfs_feeds(gtfs_root_dir: str) -> List[Tuple[str, str]]:
    """
    Discover all GTFS feeds in the root directory.
    Returns list of (agency_name, stops_file_path) tuples.
    """
    gtfs_feeds = []
    
    if not os.path.exists(gtfs_root_dir):
        print(f"GTFS directory not found: {gtfs_root_dir}")
        return gtfs_feeds
    
    for item in os.listdir(gtfs_root_dir):
        item_path = os.path.join(gtfs_root_dir, item)
        
        # Skip files, only process directories
        if not os.path.isdir(item_path):
            continue
        
        # Look for stops.txt in this directory
        stops_file = os.path.join(item_path, 'stops.txt')
        if os.path.exists(stops_file):
            # Extract agency name from directory name
            agency_name = item.replace('_GTFS', '').replace('-GTFS', '').upper()
            gtfs_feeds.append((agency_name, stops_file))
            print(f"Found GTFS feed: {agency_name} at {stops_file}")
    
    return gtfs_feeds

def load_stops_from_gtfs(file_path: str, agency_prefix: str) -> List[Dict]:
    """Load stops from a GTFS stops.txt file."""
    stops = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip rows with missing coordinates
                if not row.get('stop_lat') or not row.get('stop_lon'):
                    continue
                
                stop = {
                    'stop_id': f"{agency_prefix}_{row['stop_id']}",
                    'original_stop_id': row['stop_id'],
                    'stop_name': row['stop_name'].strip(),
                    'stop_lat': float(row['stop_lat']),
                    'stop_lon': float(row['stop_lon']),
                    'agency': agency_prefix,
                    'stop_code': row.get('stop_code', ''),
                    'zone_id': row.get('zone_id', ''),
                    'stop_url': row.get('stop_url', ''),
                    'wheelchair_boarding': row.get('wheelchair_boarding', ''),
                    'platform_code': row.get('platform_code', ''),
                }
                stops.append(stop)
    except FileNotFoundError:
        print(f"Warning: Could not find {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return stops

def cluster_stops_by_proximity(stops: List[Dict], max_distance: float = 100) -> List[List[Dict]]:
    """Group stops that are within max_distance meters of each other."""
    clusters = []
    used_stops = set()
    
    for i, stop in enumerate(stops):
        if i in used_stops:
            continue
        
        # Start a new cluster with this stop
        cluster = [stop]
        used_stops.add(i)
        
        # Find all stops within max_distance
        for j, other_stop in enumerate(stops):
            if j in used_stops:
                continue
            
            distance = haversine_distance(
                stop['stop_lat'], stop['stop_lon'],
                other_stop['stop_lat'], other_stop['stop_lon']
            )
            
            if distance <= max_distance:
                cluster.append(other_stop)
                used_stops.add(j)
        
        clusters.append(cluster)
    
    return clusters

def consolidate_cluster(cluster: List[Dict], min_name_similarity: float = 0.6) -> List[Dict]:
    """
    Consolidate stops within a geographic cluster based on name similarity.
    Returns a list of consolidated stations.
    """
    if len(cluster) == 1:
        # Single stop - create station with one stop
        stop = cluster[0]
        station = {
            'station_id': f"station_{stop['stop_id']}",
            'station_name': stop['stop_name'],
            'station_lat': stop['stop_lat'],
            'station_lon': stop['stop_lon'],
            'stops': [stop]
        }
        return [station]
    
    # Group stops by name similarity
    name_groups = []
    used_stops = set()
    
    for i, stop in enumerate(cluster):
        if i in used_stops:
            continue
        
        # Start a new name group
        group = [stop]
        used_stops.add(i)
        
        # Find stops with similar names
        for j, other_stop in enumerate(cluster):
            if j in used_stops:
                continue
            
            similarity = name_similarity(stop['stop_name'], other_stop['stop_name'])
            if similarity >= min_name_similarity:
                group.append(other_stop)
                used_stops.add(j)
        
        name_groups.append(group)
    
    # Create consolidated stations
    stations = []
    for group in name_groups:
        # Calculate centroid coordinates
        avg_lat = sum(stop['stop_lat'] for stop in group) / len(group)
        avg_lon = sum(stop['stop_lon'] for stop in group) / len(group)
        
        # Choose the best name with smarter logic
        def score_name(stop_name):
            name = stop_name.lower()
            base_score = 100  # Start with a base score
            
            # Heavy penalties for overly specific terms
            if 'bus' in name and ('go' in name or 'station' in name or 'terminal' in name):
                base_score -= 50  # "Unionville GO Bus" vs "Unionville GO"
            if 'platform' in name:
                base_score -= 30
            if name.count(' ') > 4:  # Too many words
                base_score -= 20
            
            # Penalize names with major hub in brackets - prefer the hub name itself
            if '(' in stop_name and ')' in stop_name:
                # Extract content in brackets
                bracket_content = stop_name[stop_name.find('(')+1:stop_name.find(')')].lower()
                # If brackets contain major hub indicators, penalize this name
                hub_indicators = ['station', 'terminal', 'go', 'transit', 'centre', 'center']
                if any(indicator in bracket_content for indicator in hub_indicators):
                    base_score -= 40  # "Local Stop (Union Station)" vs "Union Station"
            
            # Rewards for good descriptive terms
            if 'university' in name and len(name) > 15:
                base_score += 40  # "University of Waterloo" vs "UW"
            if 'station' in name and 'bus' not in name and '(' not in name:
                base_score += 20  # "Union Station" is good, but not if it's in brackets
            if 'terminal' in name and 'bus' not in name and '(' not in name:
                base_score += 15
            
            # Prefer moderate lengths (not too short, not too long)
            length = len(stop_name)
            if 10 <= length <= 25:  # Sweet spot
                base_score += 10
            elif length < 5:  # Too short like "UW"
                base_score -= 30
            elif length > 40:  # Too long
                base_score -= 20
            
            return base_score
        
        best_name = max(group, key=lambda s: score_name(s['stop_name']))['stop_name']
        
        # Create clean, URL-friendly station ID
        clean_name = normalize_stop_name(best_name)
        # Remove special characters and replace spaces/slashes with hyphens
        station_id = clean_name.replace('/', '-').replace(' ', '-').replace('_', '-')
        # Remove multiple consecutive hyphens and clean up
        station_id = re.sub(r'-+', '-', station_id).strip('-')
        # Add numeric suffix if needed for uniqueness (simple approach)
        station_id = f"stn-{station_id}"
        
        station = {
            'station_id': station_id,
            'station_name': best_name,
            'station_lat': avg_lat,
            'station_lon': avg_lon,
            'stops': group
        }
        stations.append(station)
    
    return stations

def main():
    """Main consolidation process."""
    print("Station Consolidation Script")
    print("=" * 40)
    
    # Discover all GTFS feeds
    gtfs_root_dir = 'backend/data/GTFS'
    print(f"Discovering GTFS feeds in {gtfs_root_dir}...")
    gtfs_feeds = discover_gtfs_feeds(gtfs_root_dir)
    
    if not gtfs_feeds:
        print("No GTFS feeds found! Make sure you have directories with stops.txt files.")
        return
    
    print(f"Found {len(gtfs_feeds)} GTFS feeds")
    
    # Load stops from all GTFS feeds
    all_stops = []
    
    for agency_name, stops_file in gtfs_feeds:
        stops = load_stops_from_gtfs(stops_file, agency_name)
        all_stops.extend(stops)
        print(f"Loaded {len(stops)} stops from {agency_name}")
    
    print(f"Total stops loaded: {len(all_stops)}")
    
    # Cluster stops by proximity
    print("\nClustering stops by geographic proximity (200m radius)...")
    proximity_clusters = cluster_stops_by_proximity(all_stops, max_distance=200)
    print(f"Found {len(proximity_clusters)} geographic clusters")
    
    # Consolidate each cluster by name similarity
    print("Consolidating stops within clusters by name similarity...")
    all_stations = []
    
    for cluster in proximity_clusters:
        stations = consolidate_cluster(cluster)
        all_stations.extend(stations)
    
    print(f"Created {len(all_stations)} consolidated stations")
    
    # Save consolidated stations
    output_file = 'backend/static/consolidated_stations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_stations, f, indent=2, ensure_ascii=False)
    
    print(f"Saved consolidated stations to {output_file}")
    
    # Print some examples
    print("\n" + "=" * 40)
    print("Example consolidated stations:")
    
    # Find University of Waterloo examples
    uw_stations = [s for s in all_stations if 'waterloo' in s['station_name'].lower() and 'university' in s['station_name'].lower()]
    for station in uw_stations[:2]:
        print(f"\nStation: {station['station_name']}")
        print(f"  Location: ({station['station_lat']:.6f}, {station['station_lon']:.6f})")
        print(f"  Consolidated {len(station['stops'])} stops:")
        for stop in station['stops']:
            print(f"    - {stop['agency']}: {stop['original_stop_id']} - {stop['stop_name']}")
    
    # Find Bramalea examples
    bramalea_stations = [s for s in all_stations if 'bramalea' in s['station_name'].lower()]
    for station in bramalea_stations[:2]:
        print(f"\nStation: {station['station_name']}")
        print(f"  Location: ({station['station_lat']:.6f}, {station['station_lon']:.6f})")
        print(f"  Consolidated {len(station['stops'])} stops:")
        for stop in station['stops']:
            print(f"    - {stop['agency']}: {stop['original_stop_id']} - {stop['stop_name']}")
    
    # Show statistics
    multi_stop_stations = [s for s in all_stations if len(s['stops']) > 1]
    multi_agency_stations = [s for s in all_stations if len(set(stop['agency'] for stop in s['stops'])) > 1]
    
    print(f"\n" + "=" * 40)
    print("Consolidation Statistics:")
    print(f"  Total stations: {len(all_stations)}")
    print(f"  Single-stop stations: {len(all_stations) - len(multi_stop_stations)}")
    print(f"  Multi-stop stations: {len(multi_stop_stations)}")
    print(f"  Multi-agency stations: {len(multi_agency_stations)}")

if __name__ == "__main__":
    main()