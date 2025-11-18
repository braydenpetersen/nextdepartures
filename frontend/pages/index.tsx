import React, { useEffect, useState, useRef } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { GetServerSideProps } from 'next';
import { DepartureRow } from '../components/DepartureRow';
import { DepartureHeader } from '../components/DepartureHeader';
import { StationSearch } from '../components/StationSearch';
import { NetworkGroup, RouteGroup, Station } from '../types';
import GoTransitLogo from '../components/svg/gotransit_logo.svg';
import GrtLogo from '../components/svg/grt_logo_white.svg';

interface PageProps {
  stationName?: string;
}

function Index({ stationName: serverStationName }: PageProps) {
  const router = useRouter();
  const isInitialLoad = useRef(true);

  const [departures, setDepartures] = useState<NetworkGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stationName, setStationName] = useState<string>(serverStationName || '');

  useEffect(() => {
    if (!router.isReady) return;

    // Only fetch departures if stops are provided in the URL
    if (!router.query.stops || router.query.stops === '') {
      setIsLoading(false);
      setDepartures([]);
      return;
    }

    const fetchDepartures = () => {
      const stops = router.query.stops;
      const apiQuery = `/api/departures?stops=${stops}`;

      if (isInitialLoad.current) {
        setIsLoading(true);
      }

      fetch(apiQuery)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          setDepartures(data);
          setIsLoading(false);
          isInitialLoad.current = false;
        })
        .catch(error => {
          console.error('Error fetching departures:', error);
          setIsLoading(false);
        });
    };

    fetchDepartures();
    const interval = setInterval(fetchDepartures, 30000);

    return () => clearInterval(interval);
  }, [router.isReady, router.query.stops]);

  // Fetch station name based on stops
  useEffect(() => {
    if (!router.isReady || !router.query.stops) {
      setStationName('');
      return;
    }

    const stops = router.query.stops as string;
    const stopIds = stops.split(',');

    // Extract first stop's agency and code for search
    if (stopIds.length > 0) {
      const firstStop = stopIds[0];
      const agency = firstStop.split('_')[0];

      // Search for stations containing this stop
      fetch(`/api/stations?q=${agency}&limit=20`)
        .then(response => response.json())
        .then(data => {
          if (data.stations && data.stations.length > 0) {
            // Find station that contains all our stops
            const matchingStation = data.stations.find((station: Station) => {
              const stationStopIds = station.stops.map(s => s.stop_id);
              return stopIds.every(id => stationStopIds.includes(id));
            });

            if (matchingStation) {
              setStationName(matchingStation.station_name);
            } else {
              setStationName('Departures');
            }
          }
        })
        .catch(error => {
          console.error('Error fetching station name:', error);
          setStationName('Departures');
        });
    }
  }, [router.isReady, router.query.stops]);

  const [ctime, setCtime] = useState('');

  useEffect(() => {
    setCtime(
      new Date().toLocaleTimeString('en-GB', {
        timeZone: 'America/Toronto',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    );

    const timer = setInterval(() => {
      setCtime(
        new Date().toLocaleTimeString('en-GB', {
          timeZone: 'America/Toronto',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const isGrtIon = (routeGroup: RouteGroup) => {
    return (
      routeGroup.routeNetwork === 'GRT' && routeGroup.routeNumber === '301'
    );
  };

  const getNetworkLogo = (network: string) => {
    switch (network) {
      case 'GO':
        return GoTransitLogo;
      case 'GRT':
        return GrtLogo;
      default:
        return null;
    }
  };

  // Show search page if no stops in URL
  if (!router.query.stops || router.query.stops === '') {
    return (
      <>
        <Head>
          <title>nextdepartures - Real-time Transit Departures</title>
        </Head>
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
          <div className="w-full max-w-2xl text-center">
            <h1 className="text-4xl sm:text-6xl font-bold mb-4 text-white">
              nextdepartures
            </h1>
            <p className="text-xl text-[var(--light-grey)] mb-8">
              Real-time transit departures for GO Transit and Grand River Transit
            </p>
            <StationSearch />
            <p className="text-sm text-[var(--light-grey)] mt-6">
              Search for any station or stop
            </p>
          </div>
        </div>
      </>
    );
  }

  // Generate dynamic OG image URL for stops
  const generateOGImageUrl = (stops: string, name?: string) => {
    const baseUrl = process.env.NODE_ENV === 'production'
      ? 'https://transit.braydenpetersen.com'
      : 'http://localhost:3000';
    const url = `${baseUrl}/api/og-image?stops=${encodeURIComponent(stops)}${name ? `&name=${encodeURIComponent(name)}` : ''}`;
    console.log('Generated OG image URL:', url); // Debug log
    return url;
  };

  // Show departure board if station is provided
  return (
    <>
      <Head>
        <title>
          {stationName 
            ? `${stationName} - Live Departures` 
            : 'Live Departure Board - Real-time Transit Departures'
          }
        </title>
        {router.query.stops ? (
          <>
            {/* Station-specific meta tags */}
            <meta property="og:title" content={stationName ? `${stationName} - Live Departures` : 'Live Departure Board'} />
            <meta property="og:description" content={`Real-time transit departures ${stationName ? `for ${stationName}` : 'for GO Transit and Grand River Transit'}`} />
            <meta property="og:image" content={generateOGImageUrl(router.query.stops as string, stationName)} />
            <meta property="twitter:title" content={stationName ? `${stationName} - Live Departures` : 'Live Departure Board'} />
            <meta property="twitter:description" content={`Real-time transit departures ${stationName ? `for ${stationName}` : 'for GO Transit and Grand River Transit'}`} />
            <meta property="twitter:image" content={generateOGImageUrl(router.query.stops as string, stationName)} />
          </>
        ) : (
          <>
            {/* Homepage meta tags */}
            <meta property="og:title" content="nextdepartures" />
            <meta property="og:description" content="Real-time transit departures for GO Transit and Grand River Transit" />
            <meta property="og:image" content="https://transit.braydenpetersen.com/og-image.png" />
            <meta property="twitter:title" content="nextdepartures" />
            <meta property="twitter:description" content="Real-time transit departures for GO Transit and Grand River Transit" />
            <meta property="twitter:image" content="https://transit.braydenpetersen.com/og-image.png" />
          </>
        )}
      </Head>
      <div className="mx-3 font-bold tracking-tight">
      {isLoading && isInitialLoad.current ? (
        <div className="h-32 sm:h-40 flex items-center justify-center text-[var(--light-grey)] text-xl sm:text-2xl">
          Loading departures...
        </div>
      ) : (
        <>
          {departures.map((networkGroup, networkIndex) => {
            const Logo = getNetworkLogo(networkGroup.network);
            // Filter out routes with old departures (countdown < -1) as a safety measure
            const validRoutes = networkGroup.routes
              .map(route => ({
                ...route,
                departures: route.departures.filter(d => d.countdown >= -1)
              }))
              .filter(route => route.departures.length > 0);

            // Skip this network if no valid routes remain
            if (validRoutes.length === 0) return null;

            return (
              <div key={networkGroup.network} className="mb-8">
                <div
                  className="flex justify-between items-center w-full h-[52px]"
                  style={{ lineHeight: '100%' }}
                >
                  <div className="flex items-center gap-4">
                    {Logo && (
                      <div className="flex items-center justify-center w-[45px] h-[52px]">
                        <Logo className="w-[45px] h-full -mt-1" />
                      </div>
                    )}
                    <div className="flex items-center h-full">
                      <h2 className="text-xl tracking-tight">
                        Departures
                        <span className="font-normal"> | Départs</span>
                      </h2>
                    </div>
                  </div>
                  <div className="flex items-center h-full text-[var(--light-grey)]">
                    <h2
                      className="text-xl tracking-tight"
                      style={{ fontVariantNumeric: 'tabular-nums' }}
                    >
                      {ctime}
                    </h2>
                  </div>
                </div>
                {networkIndex === 0 && <DepartureHeader />}
                {validRoutes.map((routeGroup, routeIndex) => (
                  <DepartureRow
                    key={`${networkGroup.network}-${routeGroup.routeNumber}-${routeGroup.headsign}`}
                    routeGroup={routeGroup}
                    index={networkIndex * 100 + routeIndex}
                    isGrtIon={isGrtIon}
                  />
                ))}
              </div>
            );
          })}
        </>
      )}
      </div>
    </>
  );
}

export const getServerSideProps: GetServerSideProps<PageProps> = async (context) => {
  const { stops } = context.query;

  if (!stops || typeof stops !== 'string') {
    return {
      props: {}
    };
  }

  try {
    const stopIds = stops.split(',');
    if (stopIds.length === 0) {
      return { props: {} };
    }

    // Extract first stop's agency for search
    const firstStop = stopIds[0];
    const agency = firstStop.split('_')[0];

    // Try to fetch proper station name from API
    const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8080';
    const apiKey = process.env.API_KEY;

    if (!apiKey) {
      console.error('API_KEY not configured');
      return { props: {} };
    }

    const response = await fetch(`${apiUrl}/api/stations/search?q=${encodeURIComponent(agency)}&limit=20`, {
      headers: {
        'X-API-Key': apiKey
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.stations && data.stations.length > 0) {
        // Find station that contains all our stops
        const matchingStation = data.stations.find((station: Station) => {
          const stationStopIds = station.stops.map((s: { stop_id: string }) => s.stop_id);
          return stopIds.every((id: string) => stationStopIds.includes(id));
        });

        if (matchingStation) {
          return {
            props: {
              stationName: matchingStation.station_name
            }
          };
        }
      }
    }

    return { props: {} };

  } catch (error) {
    console.error('Error fetching station data:', error);
    return { props: {} };
  }
};

export default Index;
