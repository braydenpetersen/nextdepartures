from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Departure:
    """Standardized departure data structure"""
    stop_id: str
    route_number: str
    headsign: str
    platform: Optional[str]
    route_network: str
    time: str
    countdown: int
    branch_code: str
    route_color: Optional[str]
    route_text_color: Optional[str]

class TransitPlugin(ABC):
    """Base class for all transit network plugins"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    @property
    @abstractmethod
    def network_name(self) -> str:
        """Return the network identifier (e.g., 'GO', 'GRT', 'TTC')"""
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Whether this network requires an API key"""
        pass
    
    @abstractmethod
    def get_departures(self, stop_id: str) -> List[Departure]:
        """
        Fetch departures for a given stop ID.
        Should handle all network-specific API calls and data transformation.
        """
        pass
    
    @abstractmethod
    def get_route_colors(self, route_number: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get route colors for a given route.
        Returns (route_color, route_text_color) tuple.
        """
        pass
    
    def validate_stop_id(self, stop_id: str) -> bool:
        """Validate if a stop ID is valid for this network"""
        return True  # Default implementation
    
    def transform_stop_id(self, raw_stop_id: str) -> str:
        """Transform raw stop ID to network-specific format if needed"""
        return raw_stop_id
    
    def get_network_config(self) -> Dict:
        """Return network-specific configuration"""
        return self.config