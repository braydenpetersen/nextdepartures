import os
from typing import Dict, List, Optional
from .base_plugin import TransitPlugin, Departure
from .go_transit import GOTransitPlugin
from .grt import GRTPlugin

class PluginManager:
    """Manages transit plugins and routes requests to appropriate networks"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.plugins: Dict[str, TransitPlugin] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Load and initialize all available plugins"""
        try:
            # Load GO Transit plugin
            go_config = {
                'api_key': self.config.get('GO_API_KEY')
            }
            if go_config['api_key']:
                self.plugins['GO'] = GOTransitPlugin(go_config)
                print("Loaded GO Transit plugin")
            else:
                print("Warning: GO Transit plugin not loaded - missing API key")
            
            # Load GRT plugin (no API key required)
            self.plugins['GRT'] = GRTPlugin()
            print("Loaded GRT plugin")
            
        except Exception as e:
            print(f"Error loading plugins: {e}")
    
    def get_network_from_stop_id(self, stop_id: str) -> Optional[str]:
        """Extract network name from stop ID (e.g., 'GO_UN' -> 'GO')"""
        if '_' in stop_id:
            return stop_id.split('_', 1)[0].upper()
        return None
    
    def get_departures_for_stops(self, stop_ids: List[str]) -> List[Departure]:
        """Get departures for multiple stops, routing to appropriate plugins"""
        all_departures = []
        
        # Group stop IDs by network
        network_stops = {}
        for stop_id in stop_ids:
            network = self.get_network_from_stop_id(stop_id)
            if network and network in self.plugins:
                if network not in network_stops:
                    network_stops[network] = []
                # Extract the actual stop ID (remove network prefix)
                actual_stop_id = stop_id.split('_', 1)[1] if '_' in stop_id else stop_id
                network_stops[network].append(actual_stop_id)
            else:
                print(f"Warning: No plugin found for stop {stop_id}")
        
        # Fetch departures from each network
        for network, actual_stop_ids in network_stops.items():
            plugin = self.plugins[network]
            try:
                if network == 'GRT':
                    # GRT supports batch requests
                    departures = plugin.get_departures(actual_stop_ids)
                    all_departures.extend(departures)
                else:
                    # Other networks process one stop at a time
                    for actual_stop_id in actual_stop_ids:
                        departures = plugin.get_departures(actual_stop_id)
                        all_departures.extend(departures)
            except Exception as e:
                print(f"Error getting departures from {network}: {e}")
        
        return all_departures
    
    def get_available_networks(self) -> List[str]:
        """Get list of available network names"""
        return list(self.plugins.keys())
    
    def get_plugin(self, network: str) -> Optional[TransitPlugin]:
        """Get a specific plugin by network name"""
        return self.plugins.get(network.upper())
    
    def is_network_available(self, network: str) -> bool:
        """Check if a network plugin is available"""
        return network.upper() in self.plugins