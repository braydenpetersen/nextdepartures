import React, { useEffect, useState, useRef } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { DepartureRow } from '../components/DepartureRow';
import { DepartureHeader } from '../components/DepartureHeader';
import { StationSearch } from '../components/StationSearch';
import { NetworkGroup, RouteGroup } from '../types';
import GoTransitLogo from '../components/svg/gotransit_logo.svg';
import GrtLogo from '../components/svg/grt_logo_white.svg';

function Index() {
  const router = useRouter();
  const isInitialLoad = useRef(true);

  const [departures, setDepartures] = useState<NetworkGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!router.isReady) return;

    // Only fetch departures if station is provided in the URL
    if (!router.query.station || router.query.station === '') {
      setIsLoading(false);
      setDepartures([]);
      return;
    }

    const fetchDepartures = () => {
      const station = router.query.station;
      const apiQuery = `/api/departures?station=${station}`;

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
  }, [router.isReady, router.query.station]);

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

  // Show search page if no station in URL
  if (!router.query.station || router.query.station === '') {
    return (
      <>
        <Head>
          <title>Live Departure Board - Real-time Transit Departures</title>
        </Head>
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
          <div className="w-full max-w-2xl text-center">
            <h1 className="text-4xl sm:text-6xl font-bold mb-4 text-white">
              UW Departures
            </h1>
            <p className="text-xl text-[var(--light-grey)] mb-8">
              Real-time transit departures for University of Waterloo
            </p>
            <StationSearch />
            <p className="text-sm text-[var(--light-grey)] mt-6">
              Search for any GO Transit or Grand River Transit station
            </p>
          </div>
        </div>
      </>
    );
  }

  // Show departure board if station is provided
  return (
    <>
      <Head>
        <title>Live Departure Board - Real-time Transit Departures</title>
      </Head>
      <div className="mx-3 font-bold tracking-tight">
      {/* Search bar at top when showing departures */}
      <div className="mb-6 pt-4">
        <StationSearch />
      </div>

      {isLoading && isInitialLoad.current ? (
        <div className="h-32 sm:h-40 flex items-center justify-center text-[var(--light-grey)] text-xl sm:text-2xl">
          Loading departures...
        </div>
      ) : (
        <>
          {departures.map((networkGroup, networkIndex) => {
            const Logo = getNetworkLogo(networkGroup.network);
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
                {networkGroup.routes.map((routeGroup, routeIndex) => (
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

export default Index;
