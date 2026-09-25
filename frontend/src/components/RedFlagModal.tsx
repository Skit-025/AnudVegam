/**
 * Clinical Red-Flag Emergency Modal Component
 * ============================================
 * 
 * File Purpose:
 * -------------
 * Displays high-priority visual alerts when Dialogue AI detects acute danger symptoms
 * (e.g. cardiac distress, altered sensorium, sudden breathing difficulty).
 * 
 * Connected to:
 * -------------
 * - `frontend/src/pages/Converse/ConversePage.tsx`: Triggered when question response contains red flag alert.
 */

import React from 'react';

interface RedFlagModalProps {
  isOpen: boolean;
  reason?: string;
  onDismiss: () => void;
  onEscalateToNurse: () => void;
}

export const RedFlagModal: React.FC<RedFlagModalProps> = ({
  isOpen,
  reason = 'Acute clinical symptom reported requiring immediate triage.',
  onDismiss,
  onEscalateToNurse
}) => {
  if (!isOpen) return null;

  // Step 1: Render emergency modal dialog with audio chime or high-visibility red badge.
  // Step 2: Provide action buttons to notify OPD nurse station or proceed with care.
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border-2 border-red-500 space-y-4">
        <h3 className="text-xl font-bold text-red-600">🚨 Attention: Priority Symptom Detected</h3>
        <p className="text-gray-700">{reason}</p>
        <p className="text-sm text-gray-500">OPD nursing staff has been alerted for priority evaluation.</p>
        <div className="flex justify-end space-x-3 pt-2">
          <button onClick={onDismiss} className="px-4 py-2 border rounded-lg text-gray-600">
            Continue Interview
          </button>
          <button onClick={onEscalateToNurse} className="px-4 py-2 bg-red-600 text-white font-semibold rounded-lg">
            Call OPD Staff
          </button>
        </div>
      </div>
    </div>
  );
};
