import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { DepartureRow } from '../components/DepartureRow';
import { DepartureHeader } from '../components/DepartureHeader';

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

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

  const [departures, setDepartures] = useState<RouteGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!router.isReady) return;

    const fetchDepartures = () => {
      const stopCode = router.query.stopCode || '02799';
      const apiQuery = `${apiUrl}?stopCode=${stopCode}`;

      setIsLoading(true);
      fetch(apiQuery)
        .then(response => response.json())
        .then(data => {
          setDepartures(data);
          setIsLoading(false);
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

  return (
    <div className="mx-2 font-bold tracking-tight">
      <div
        className="flex justify-between items-center py-10 w-full"
        style={{ lineHeight: '100%' }}
      >
        <div>
          <h1 className="text-[30px] sm:text-[40px] tracking-tight h-full">
            Departures
            <span className="font-normal"> | Départs</span>
          </h1>
        </div>
        <div className="text-[var(--light-grey)]">
          <h1
            className="text-[30px] sm:text-[40px] tracking-tight h-full"
            style={{ fontVariantNumeric: 'tabular-nums' }}
          >
            {ctime}
          </h1>
        </div>
      </div>
      <div className="flex w-full">
        <div className="flex-1">
          <DepartureHeader />
          {isLoading ? (
            <div className="h-32 sm:h-40 flex items-center justify-center text-[var(--light-grey)] text-xl sm:text-2xl">
              Loading departures...
            </div>
          ) : (
            <div>
              {departures.map((routeGroup, index) => (
                <DepartureRow
                  key={index}
                  routeGroup={routeGroup}
                  index={index}
                  isGrtIon={isGrtIon}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Index;
