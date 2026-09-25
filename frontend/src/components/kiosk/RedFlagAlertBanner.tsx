/**
 * Clinical Red-Flag Alert Banner
 * ==============================
 * 
 * Enforces prompt specification §17:
 * Distinctive warning banner prioritizing clinical review without making an autonomous diagnosis.
 */

import React from 'react';
import { AlertCircle, ArrowRight } from 'lucide-react';

interface RedFlagAlertBannerProps {
  reason?: string | null;
  severity?: string;
  onAcknowledge?: () => void;
}

export const RedFlagAlertBanner: React.FC<RedFlagAlertBannerProps> = ({
  reason = 'Some of your responses indicate symptoms that require prompt clinical assessment.',
  severity = 'CRITICAL',
  onAcknowledge
}) => {
  return (
    <div className="bg-red-50 border-2 border-red-500 rounded-2xl p-5 my-5 shadow-lg animate-subtle-pulse">
      <div className="flex items-start space-x-4">
        <div className="p-2.5 bg-red-600 text-white rounded-xl shadow-md">
          <AlertCircle className="w-7 h-7" />
        </div>

        <div className="flex-1 space-y-1">
          <div className="flex items-center space-x-2">
            <span className="bg-red-600 text-white text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              Priority Clinical Review
            </span>
            <span className="text-xs font-semibold text-red-700">Severity: {severity}</span>
          </div>

          <h3 className="text-lg font-bold text-red-950">
            Recorded for Priority Attention
          </h3>

          <p className="text-sm text-red-900 leading-relaxed font-medium">
            {reason}
          </p>

          <p className="text-xs text-red-700 pt-1">
            ✓ Your responses are safely recorded and have been flagged for your doctor's queue.
          </p>
        </div>

        {onAcknowledge && (
          <button
            onClick={onAcknowledge}
            className="self-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-xl transition flex items-center space-x-1.5 shadow-sm"
          >
            <span>Understood</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
