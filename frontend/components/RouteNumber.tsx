import React from 'react';
import { RouteGroup } from '@/types';
import { GrtIonLogo } from './svg';

interface RouteNumberProps {
  routeGroup: RouteGroup;
  isGrtIon: (routeGroup: RouteGroup) => boolean;
}

export const RouteNumber: React.FC<RouteNumberProps> = ({
  routeGroup,
  isGrtIon,
}) => {
  if (isGrtIon(routeGroup)) {
    return (
      <GrtIonLogo className="text-[45px] sm:text-[60px] inline-block align-middle" />
    );
  }

  return (
    <div
      className="text-[22px] sm:text-[30px] text-center font-lining rounded-[10px] flex-shrink-0 justify-center w-fit px-[8px] sm:px-[10px] min-w-[50px] sm:min-w-[70px]"
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
