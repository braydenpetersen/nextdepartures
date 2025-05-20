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
