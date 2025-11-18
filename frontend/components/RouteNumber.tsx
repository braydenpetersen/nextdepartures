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
      className="text-center font-lining flex-shrink-0 justify-center w-fit text-departure"
      style={{
        color: routeGroup.routeTextColor,
        backgroundColor: routeGroup.routeColor,
        borderRadius: 'clamp(6px, 1vw, 20px)',
        padding: 'clamp(1px, 0.3vw, 6px) clamp(6px, 1.2vw, 24px) clamp(0.5px, 0.2vw, 4px)',
        minWidth: 'clamp(30px, 5vw, 100px)',
      }}
    >
      {routeGroup.routeNumber}
      {routeGroup.branchCode}
    </div>
  );
};
