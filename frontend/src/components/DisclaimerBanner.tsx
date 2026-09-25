/**
 * AI Safety Disclaimer Banner Component
 * =====================================
 * 
 * File Purpose:
 * -------------
 * Renders the mandatory clinical safety alert on all AI-assisted screens
 * (Summary review, Consult preview, Kiosk questionnaire).
 * 
 * Connected to:
 * -------------
 * - `frontend/src/pages/Summary/SummaryPage.tsx`
 * - `frontend/src/pages/Consult/ConsultPage.tsx`
 */

import React from 'react';

interface DisclaimerBannerProps {
  customText?: string;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({
  customText = 'AI-drafted. Physician review required before use. This system does not diagnose or prescribe.'
}) => {
  // Step 1: Render prominent warning box with warning icon and high-contrast text.
  return (
    <div className="bg-amber-50 border-l-4 border-amber-500 p-4 my-4 rounded-md shadow-sm">
      <div className="flex items-center space-x-3">
        <span className="text-amber-600 font-bold text-lg">⚠️</span>
        <span className="text-sm font-medium text-amber-900">{customText}</span>
      </div>
    </div>
  );
};
