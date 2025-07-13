import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Station, StationSearchResponse } from '../types';

interface StationSearchProps {
  onStationSelect?: (station: Station) => void;
}

export function StationSearch({ onStationSelect }: StationSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [stations, setStations] = useState<Station[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  useEffect(() => {
    if (query.trim().length < 2) {
      setStations([]);
      setIsDropdownOpen(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/stations?q=${encodeURIComponent(query)}&limit=8`);
        if (response.ok) {
          const data: StationSearchResponse = await response.json();
          setStations(data.stations);
          setIsDropdownOpen(data.stations.length > 0);
          setSelectedIndex(-1);
        }
      } catch (error) {
        console.error('Error searching stations:', error);
        setStations([]);
        setIsDropdownOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleStationSelect = (station: Station) => {
    const stopCodes = station.stops
      .filter(stop => stop.stop_id && stop.stop_id.trim() !== '')
      .map(stop => stop.stop_id)
      .join(',');
    
    if (stopCodes) {
      // Clear current URL first to trigger departure clearing, then navigate to new station
      router.push('/').then(() => {
        router.push(`/?stops=${stopCodes}`);
      });
    }
    
    setQuery(station.station_name);
    setIsDropdownOpen(false);
    setSelectedIndex(-1);
    
    if (onStationSelect) {
      onStationSelect(station);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen || stations.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, stations.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < stations.length) {
          handleStationSelect(stations[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const getAgencyDisplay = (agencies: string[]) => {
    const uniqueAgencies = [...new Set(agencies)];
    return uniqueAgencies.join(' • ');
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-md mx-auto">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && stations.length > 0 && setIsDropdownOpen(true)}
          placeholder="Search stations..."
          className="w-full px-4 py-3 text-lg bg-[var(--dark-grey)] text-white rounded-lg border border-[var(--light-grey)] focus:outline-none focus:border-[var(--light-green)] transition-colors"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="w-5 h-5 border-2 border-[var(--light-grey)] border-t-[var(--light-green)] rounded-full animate-spin"></div>
          </div>
        )}
      </div>

      {isDropdownOpen && stations.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-[var(--dark-grey)] border border-[var(--light-grey)] rounded-lg shadow-lg max-h-80 overflow-y-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-[var(--light-grey)]">
          {stations.map((station, index) => {
            const agencies = station.stops.map(stop => stop.agency);
            const isSelected = index === selectedIndex;
            
            return (
              <div
                key={station.station_id}
                onClick={() => handleStationSelect(station)}
                className={`px-4 py-3 cursor-pointer transition-colors border-b border-[var(--light-grey)] last:border-b-0 ${
                  isSelected 
                    ? 'bg-[var(--light-green)] bg-opacity-20 text-[var(--light-green)]'
                    : 'hover:bg-black hover:bg-opacity-40'
                }`}
              >
                <div className="font-semibold text-white">{station.station_name}</div>
                <div className="text-sm text-[var(--light-grey)] mt-1">
                  {getAgencyDisplay(agencies)} • {station.stops.length} stop{station.stops.length !== 1 ? 's' : ''}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}