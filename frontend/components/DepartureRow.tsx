import React from 'react';
import { RouteGroup } from '@/types';
import { RouteNumber } from '@/components/RouteNumber';

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
  const firstTwoDepartures = routeGroup.departures.slice(0, 2);
  const formattedTimes = firstTwoDepartures.map(d => d.time).join(', ');

  return (
    <div
      className="grid gap-2 sm:gap-4 h-16 sm:h-20 border-t-[4px] border-[var(--light-grey)] border-dotted border-collapse border-spacing-0 items-center animate-[fadeIn_0.4s_ease-in-out] overflow-hidden [animation-fill-mode:backwards] departure-grid"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="text-[30px] sm:text-[40px] text-[var(--light-green)] flex items-center">
        {routeGroup.platform}
      </div>

      <div className="text-left flex items-center">
        <RouteNumber routeGroup={routeGroup} isGrtIon={isGrtIon} />
      </div>

      <div className="text-left text-[30px] sm:text-[40px] flex items-center">
        {routeGroup.headsign}
      </div>

      <div className="text-[30px] sm:text-[40px] flex items-center">
        <div className="flex items-center space-x-2 sm:space-x-4 text-[var(--yellow)] ml-auto">
          <span>{formattedTimes}</span>
          <span className="font-normal opacity-30">min</span>
        </div>
      </div>
    </div>
  );
};
