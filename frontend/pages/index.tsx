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

  // Only fetch station name if not provided by SSR
  useEffect(() => {
    // If we already have a server-provided station name, use it
    if (serverStationName) {
      setStationName(serverStationName);
      return;
    }

    // Otherwise, station name will be empty
    if (!router.isReady || !router.query.stops) {
      setStationName('');
      return;
    }

    setStationName('');
  }, [router.isReady, router.query.stops, serverStationName]);

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

  // Memoize OG image URL to prevent constant regeneration
  const ogImageUrl = React.useMemo(() => {
    if (!router.query.stops) return 'https://transit.braydenpetersen.com/og-image.png';

    const baseUrl = process.env.NODE_ENV === 'production'
      ? 'https://transit.braydenpetersen.com'
      : 'http://localhost:3000';
    return `${baseUrl}/api/og-image?stops=${encodeURIComponent(router.query.stops as string)}${stationName ? `&name=${encodeURIComponent(stationName)}` : ''}`;
  }, [router.query.stops, stationName]);

  // Determine if we should show search page or departure board
  const showSearchPage = !router.query.stops || router.query.stops === '';

  // Render search page
  if (showSearchPage) {
    return (
      <>
        <Head>
          <title>nextdepartures - Real-time Transit Departures</title>
        </Head>
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
          <div className="w-full max-w-2xl text-center">
            <h1
              className="font-bold mb-4 text-white"
              style={{ fontSize: 'clamp(32px, 5vw, 80px)' }}
            >
              nextdepartures
            </h1>
            <p
              className="text-[var(--light-grey)] mb-8"
              style={{ fontSize: 'clamp(18px, 2vw, 32px)' }}
            >
              Real-time transit departures for GO Transit and Grand River Transit
            </p>
            <StationSearch />
            <p
              className="text-[var(--light-grey)] mt-6"
              style={{ fontSize: 'clamp(14px, 1.4vw, 20px)' }}
            >
              Search for any station or stop
            </p>
          </div>
        </div>
      </>
    );
  }

  // Render departure board
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
            <meta property="og:image" content={ogImageUrl} />
            <meta property="twitter:title" content={stationName ? `${stationName} - Live Departures` : 'Live Departure Board'} />
            <meta property="twitter:description" content={`Real-time transit departures ${stationName ? `for ${stationName}` : 'for GO Transit and Grand River Transit'}`} />
            <meta property="twitter:image" content={ogImageUrl} />
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
      <div
        className="font-bold tracking-tight"
        style={{
          marginLeft: 'clamp(12px, 1.2vw, 24px)',
          marginRight: 'clamp(12px, 1.2vw, 24px)'
        }}
      >
      {isLoading && isInitialLoad.current ? (
        <div
          className="flex items-center justify-center text-[var(--light-grey)]"
          style={{
            height: 'clamp(120px, 15vh, 200px)',
            fontSize: 'var(--text-xl)'
          }}
        >
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
              <div
                key={networkGroup.network}
                style={{
                  marginBottom: 'clamp(24px, 2.4vw, 48px)',
                  marginTop: networkIndex === 0 ? 'clamp(20px, 2.5vw, 50px)' : 0
                }}
              >
                <div
                  className="flex justify-between items-center w-full"
                  style={{
                    lineHeight: '100%',
                    height: 'clamp(50px, 5.5vw, 110px)'
                  }}
                >
                  <div className="flex items-center gap-4">
                    {Logo && (
                      <div
                        className="flex items-center justify-center -mt-1"
                        style={{
                          width: 'clamp(50px, 5vw, 100px)',
                          height: 'clamp(50px, 5.5vw, 110px)'
                        }}
                      >
                        <Logo
                          style={{
                            width: 'clamp(50px, 5vw, 100px)',
                            height: '100%'
                          }}
                        />
                      </div>
                    )}
                    <div className="flex items-center h-full">
                      <h2 className="tracking-tight" style={{ fontSize: 'var(--text-xl)' }}>
                        {stationName || 'Departures'}
                      </h2>
                    </div>
                  </div>
                  <div className="flex items-center h-full text-[var(--light-grey)]">
                    <h2
                      className="tracking-tight"
                      style={{
                        fontVariantNumeric: 'tabular-nums',
                        fontSize: 'var(--text-xl)'
                      }}
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

    // Try to fetch proper station name from API
    const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8080';
    const apiKey = process.env.API_KEY;

    if (!apiKey) {
      console.error('API_KEY not configured');
      return { props: {} };
    }

    // Fetch all consolidated stations and reverse-search for matching station
    // This approach works better for joint-agency stations
    const response = await fetch(`${apiUrl}/api/consolidated-stations`, {
      headers: {
        'X-API-Key': apiKey
      }
    });

    if (response.ok) {
      const stations = await response.json();
      console.log('SSR: Loaded consolidated stations:', stations?.length || 0);

      if (stations && stations.length > 0) {
        // Find station that contains ALL our stop IDs
        const matchingStation = stations.find((station: Station) => {
          const stationStopIds = station.stops.map((s: { stop_id: string }) => s.stop_id);
          const allMatch = stopIds.every((id: string) => stationStopIds.includes(id));
          if (allMatch) {
            console.log('SSR: Found matching station:', station.station_name);
          }
          return allMatch;
        });

        if (matchingStation) {
          return {
            props: {
              stationName: matchingStation.station_name
            }
          };
        } else {
          console.log('SSR: No station contained all stops:', stopIds);
        }
      }
    } else {
      console.log('SSR: API request failed:', response.status);
    }

    return { props: {} };

  } catch (error) {
    console.error('SSR: Error fetching station data:', error);
    return { props: {} };
  }
};

export default Index;
