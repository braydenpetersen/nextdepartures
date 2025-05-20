import React from 'react';

export const DepartureHeader: React.FC = () => {
  return (
    <div
      className="h-16 sm:h-20 items-center tracking-tight bg-[var(--dark-grey)] grid gap-2 sm:gap-4"
      style={{
        gridTemplateColumns: `
                    var(--col-platform-width) 
                    var(--col-route-width) 
                    var(--col-direction-width) 
                    var(--col-scheduled-width)
                `,
        '@media (min-width: 640px)': {
          gridTemplateColumns: `
                        var(--col-platform-width-desktop) 
                        var(--col-route-width-desktop) 
                        var(--col-direction-width-desktop) 
                        var(--col-scheduled-width-desktop)
                    `,
        },
      }}
    >
      <div className="text-left text-[18px] sm:text-[25px] leading-none my-0">
        <div>Pltfm.</div>
        <div className="text-[var(--light-grey)] font-normal">Quai</div>
      </div>
      <div className="text-left text-[18px] sm:text-[25px] leading-none my-0">
        <div>Route</div>
        <div className="text-[var(--light-grey)] font-normal">Ligne</div>
      </div>
      <div className="text-left text-[18px] sm:text-[25px] leading-none my-0">
        <div>Direction</div>
        <div className="text-[var(--light-grey)] font-normal">Direction</div>
      </div>
      <div className="text-right text-[18px] sm:text-[25px] leading-none my-0">
        <div>Scheduled</div>
        <div className="text-[var(--light-grey)] font-normal">Programmé</div>
      </div>
    </div>
  );
};
