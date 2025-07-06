import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import { DepartureRow } from '../components/DepartureRow';
import { DepartureHeader } from '../components/DepartureHeader';
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

    const fetchDepartures = () => {
      const stopCode = router.query.stopCode || '02799';
      const apiQuery = `/api/departures?stopCode=${stopCode}`;

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
  }, [router.isReady, router.query.stopCode]);

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

  return (
    <div className="mx-3 sm:mx-6 font-bold tracking-tight">
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
  );
}

export default Index;
