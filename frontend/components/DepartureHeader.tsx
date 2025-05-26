import React from 'react';

export const DepartureHeader: React.FC = () => {
  return (
    <div
      className="h-16 sm:h-20 items-center tracking-tight bg-[var(--dark-grey)] grid gap-2 sm:gap-4 departure-grid"
    >
      <div className="text-left leading-none my-0 text-header md:text-header-tablet lg:text-header-desktop">
        <div>Pltfm.</div>
        <div className="text-[var(--light-grey)] font-normal">Quai</div>
      </div>
      <div className="text-left leading-none my-0 text-header md:text-header-tablet lg:text-header-desktop">
        <div>Route</div>
        <div className="text-[var(--light-grey)] font-normal">Ligne</div>
      </div>
      <div className="text-left leading-none my-0 text-header md:text-header-tablet lg:text-header-desktop">
        <div>Direction</div>
        <div className="text-[var(--light-grey)] font-normal">Direction</div>
      </div>
      <div className="text-right leading-none my-0 text-header md:text-header-tablet lg:text-header-desktop">
        <div>Scheduled</div>
        <div className="text-[var(--light-grey)] font-normal">Programmé</div>
      </div>
    </div>
  );
};
