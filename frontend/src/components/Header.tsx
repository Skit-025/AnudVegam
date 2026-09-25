/**
 * MediKiosk Global Header Component
 * =================================
 * 
 * File Purpose:
 * -------------
 * Renders the top navigation and status header with hospital branding,
 * active patient identification badge, language selector, and emergency reset button.
 * 
 * Connected to:
 * -------------
 * - `frontend/src/App.tsx`
 */

import React from 'react';

interface HeaderProps {
  hospitalName?: string;
  patientName?: string;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  hospitalName = 'District Civil Hospital OPD',
  patientName,
  onReset
}) => {
  // Step 1: Render hospital title and OPD logo.
  // Step 2: Render active patient tag if logged in.
  // Step 3: Provide emergency reset / start over button.
  return (
    <header className="bg-blue-800 text-white px-8 py-4 flex justify-between items-center shadow-lg">
      <div className="flex items-center space-x-3">
        <span className="text-2xl">🏥</span>
        <div>
          <h1 className="font-bold text-lg leading-tight">MediKiosk</h1>
          <p className="text-xs text-blue-200">{hospitalName}</p>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        {patientName && (
          <span className="bg-blue-900/60 px-3 py-1 rounded-full text-xs font-medium border border-blue-400">
            Patient: {patientName}
          </span>
        )}
        <button
          onClick={onReset}
          className="text-xs bg-red-600/80 hover:bg-red-700 px-3 py-1 rounded transition"
        >
          Reset Kiosk
        </button>
      </div>
    </header>
  );
};
