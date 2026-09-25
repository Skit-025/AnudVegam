/**
 * Kiosk Workflow Step Progress Bar
 * =================================
 * 
 * File Purpose:
 * -------------
 * Visual indicator tracking the 5 steps of the patient/doctor workflow:
 * 1. Identify -> 2. Converse -> 3. Scan -> 4. Summary -> 5. Consult
 * 
 * Connected to:
 * -------------
 * - `frontend/src/App.tsx`: Mounted at top of screen to reflect active screen.
 */

import React from 'react';

interface ProgressBarProps {
  currentStep: number; // 1 to 5
}

const STEPS = ['Identify', 'Converse', 'Scan', 'Summary', 'Consult'];

export const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep }) => {
  // Step 1: Map through STEPS array.
  // Step 2: Highlight completed and current steps with distinct colors.
  return (
    <div className="w-full max-w-4xl mx-auto my-6">
      <div className="flex justify-between items-center relative">
        {STEPS.map((step, idx) => (
          <div key={step} className="flex flex-col items-center z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                idx + 1 <= currentStep ? 'bg-blue-600 text-white shadow-md' : 'bg-gray-200 text-gray-500'
              }`}
            >
              {idx + 1}
            </div>
            <span className="text-xs font-semibold mt-1 text-gray-700">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
