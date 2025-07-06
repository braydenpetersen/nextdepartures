import React from 'react';
import { RouteGroup } from '@/types';
import { RouteNumber } from '@/components/RouteNumber';
import { TrainIcon } from '@/components/svg';

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
  const formatDepartureTime = (departure: { time: string; countdown: number }, isFirst: boolean) => {
    if (departure.countdown <= 0 && isFirst) {
      return { text: 'Due', isNow: true };
    } else {
      return { text: `${departure.countdown}`, isNow: false };
    }
  };

  const formattedDepartures = routeGroup.departures
    .slice(0, 2)  // Only take first two departures
    .map((departure, index) => formatDepartureTime(departure, index === 0))
    .filter(d => d.text !== '');

  return (
    <div
      className="grid gap-2 py-4 border-t-[4px] border-[var(--light-grey)] border-dotted border-collapse border-spacing-0 items-center animate-[fadeIn_0.4s_ease-in-out] overflow-hidden [animation-fill-mode:backwards] departure-grid"
      style={{ animationDelay: `${index * 500}ms` }}
    >
      <div className="text-[var(--light-green)] flex items-center text-departure tabular-nums">
        <span className="min-w-[1.5ch]">{routeGroup.platform}</span>
        {isGrtIon(routeGroup) && (
          <TrainIcon className="w-[20px] h-[28px] text-[var(--light-green)]" />
        )}
      </div>

      <div className="text-left flex items-center">
        <RouteNumber routeGroup={routeGroup} />
      </div>

      <div className="text-left flex items-center text-departure leading-[100%] min-w-0">
        <span className="[overflow-wrap:normal] [word-break:normal] [line-break:strict] whitespace-pre-wrap">{routeGroup.headsign.replace(/([/&])/g, `$1\u200B`)}</span>
      </div>

      <div className="flex items-center">
        <div className="flex items-baseline text-[var(--yellow)] w-full justify-end text-departure pr-2">
          <span>
            {formattedDepartures.map((departure, i) => (
              <span key={i}>
                {i > 0 && ', '}
                <span 
                  className={`${departure.isNow ? 'animate-[blink_1s_ease-in-out_infinite] text-[var(--light-green)]' : ''} ${i === 1 ? 'font-normal opacity-60' : ''}`}
                  style={departure.isNow ? { animationDelay: '0s' } : undefined}
                >
                  {departure.text}
                </span>
              </span>
            ))}
          </span>
        </div>
      </div>
    </div>
  );
};
