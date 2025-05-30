import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import { DepartureRow } from '../components/DepartureRow';
import { DepartureHeader } from '../components/DepartureHeader';
import { NetworkGroup } from '../types';
import GoTransitLogo from '../components/svg/gotransit_logo.svg';
import GrtLogo from '../components/svg/grt_logo_white.svg';
interface DepartureTime {
  time: string;
  countdown: number;
}

interface RouteGroup {
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
        .then(response => response.json())
        .then(data => {
          setDepartures(data);
          setIsLoading(false);
          isInitialLoad.current = false;
          console.log(data);
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
    <div className="mx-2 font-bold tracking-tight">
      <div className="flex w-full">
        <div className="flex-1">
          {isLoading && isInitialLoad.current ? (
            <div className="h-32 sm:h-40 flex items-center justify-center text-[var(--light-grey)] text-xl sm:text-2xl">
              Loading departures...
            </div>
          ) : (
            <div>
              {departures.map((networkGroup, networkIndex) => {
                const Logo = getNetworkLogo(networkGroup.network);
                return (
                  <div key={networkGroup.network} className="mb-8">
                    <div
                      className="flex justify-between items-center w-full"
                      style={{ lineHeight: '100%' }}
                    >
                      <div className="flex items-center gap-4">
                        {Logo && (
                          <div className="w-[100px] h-[90px] sm:w-[100px] sm:h-[120px] items-center">
                            <Logo className="w-[100px] h-full" />
                          </div>
                        )}
                        <h2 className="text-[30px] sm:text-[40px] tracking-tight h-full">
                          Departures
                          <span className="font-normal"> | Départs</span>
                        </h2>
                      </div>
                      <div className="text-[var(--light-grey)]">
                        <h2
                          className="text-[30px] sm:text-[40px] tracking-tight h-full"
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Index;
