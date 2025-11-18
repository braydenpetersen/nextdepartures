import React from 'react';

export const DepartureHeader: React.FC = () => {
  return (
    <div
      className="items-center tracking-tight bg-[var(--dark-grey)] grid departure-grid"
      style={{
        gap: 'clamp(10px, 1.2vw, 24px)',
        paddingTop: 'clamp(16px, 2vw, 40px)',
        paddingBottom: 'clamp(16px, 2vw, 40px)'
      }}
    >
      <div className="text-left leading-none my-0 text-header">
        <div>Pltfm.</div>
        <div className="text-[var(--light-grey)] font-normal">Quai</div>
      </div>
      <div className="text-left leading-none my-0 text-header">
        <div>Route</div>
        <div className="text-[var(--light-grey)] font-normal">Ligne</div>
      </div>
      <div className="text-left leading-none my-0 text-header">
        <div>Direction</div>
        <div className="text-[var(--light-grey)] font-normal">Direction</div>
      </div>
      <div className="text-right leading-none my-0 text-header">
        <div>Time</div>
        <div className="text-[var(--light-grey)] font-normal">Temps</div>
      </div>
    </div>
  );
};
