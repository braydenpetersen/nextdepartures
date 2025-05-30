import React from 'react';
import { RouteGroup } from '@/types';
import { RouteNumber } from '@/components/RouteNumber';
import { TrainIcon, GrtIonLogo } from '@/components/svg';

interface DepartureRowProps {
  routeGroup: RouteGroup;
  index: number;
  isGrtIon: (routeGroup: RouteGroup) => boolean;
}

export const DepartureRow: React.FC<DepartureRowProps> = ({
  routeGroup,
  index,
  isGrtIon,
}) => {
  const formatDepartureTime = (departure: { time: string; countdown: number }) => {
    if (departure.countdown <= 0) {
      return { text: 'Due', isNow: true };
    } else {
      return { text: `${departure.countdown}`, isNow: false };
    }
    return { text: '', isNow: false };
  };

  const formattedDepartures = routeGroup.departures
    .map(formatDepartureTime)
    .filter(d => d.text !== '');

  const showMinLabel = routeGroup.departures.some(d => d.countdown <= 120);

  return (
    <div
      className="grid gap-2 sm:gap-4 h-16 sm:h-20 border-t-[4px] border-[var(--light-grey)] border-dotted border-collapse border-spacing-0 items-center animate-[fadeIn_0.4s_ease-in-out] overflow-hidden [animation-fill-mode:backwards] departure-grid"
      style={{ animationDelay: `${index * 500}ms` }}
    >
      <div className="text-[var(--light-green)] flex items-center justify-between text-departure md:text-departure-tablet lg:text-departure-desktop">
        <span>{routeGroup.platform}</span>
        {isGrtIon(routeGroup) && (
          <TrainIcon className="w-[20px] h-[28px] sm:w-[25px] sm:h-[35px] text-[var(--light-green)]" />
        )}
      </div>

      <div className="text-left flex items-center">
        <RouteNumber routeGroup={routeGroup} />
      </div>

      <div className="text-left flex items-center text-departure md:text-departure-tablet lg:text-departure-desktop">
        <span>{routeGroup.headsign}</span>
        {isGrtIon(routeGroup) && (
          <GrtIonLogo className="w-[40px] h-[40px] sm:w-[50px] sm:h-[50px] text-[var(--light-green)] ml-2" />
        )}
      </div>

      <div className="flex items-center">
        <div className="flex items-baseline space-x-2 sm:space-x-4 text-[var(--yellow)] w-full justify-end text-departure md:text-departure-tablet lg:text-departure-desktop">
          <span>
            {formattedDepartures.map((departure, i) => (
              <span key={i}>
                {i > 0 && ', '}
                <span 
                  className={departure.isNow ? 'animate-[blink_1s_ease-in-out_infinite] text-[var(--light-green)]' : ''}
                  style={departure.isNow ? { animationDelay: '0s' } : undefined}
                >
                  {departure.text}
                </span>
              </span>
            ))}
          </span>
          {showMinLabel && <span className="font-normal opacity-60 text-min-label md:text-min-label-tablet lg:text-min-label-desktop">min</span>}
        </div>
      </div>
    </div>
  );
};
