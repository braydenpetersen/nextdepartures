export interface DepartureTime {
  time: string;
  countdown: number;
}

export interface RouteGroup {
  branchCode: string;
  headsign: string;
  platform: string;
  routeColor: string;
  routeNetwork: string;
  routeNumber: string;
  routeTextColor: string;
  stopCode: string;
  departures: DepartureTime[];
}

export interface NetworkGroup {
  network: string;
  routes: RouteGroup[];
}

export interface Stop {
  agency: string;
  stop_id: string;
  stop_code: string;
  stop_name: string;
}

export interface Station {
  station_id: string;
  station_name: string;
  station_lat: number;
  station_lon: number;
  stops: Stop[];
}

export interface StationSearchResponse {
  query: string;
  total_results: number;
  stations: Station[];
}
