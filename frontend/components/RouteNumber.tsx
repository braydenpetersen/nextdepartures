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
      className="text-center font-lining rounded-[10px] flex-shrink-0 justify-center w-fit px-[8px] min-w-[50px] text-departure"
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
