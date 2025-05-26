import React from 'react';
import { RouteGroup } from '@/types';

interface RouteNumberProps {
  routeGroup: RouteGroup;
}

export const RouteNumber: React.FC<RouteNumberProps> = ({
  routeGroup,
}) => {
  return (
    <div
      className="text-center font-lining rounded-[10px] flex-shrink-0 justify-center w-fit px-[8px] sm:px-[10px] min-w-[50px] sm:min-w-[70px] text-departure md:text-departure-tablet lg:text-departure-desktop"
      style={{
        color: routeGroup.routeTextColor,
        backgroundColor: routeGroup.routeColor,
      }}
    >
      {routeGroup.routeNumber}
      {routeGroup.branchCode}
    </div>
  );
};
