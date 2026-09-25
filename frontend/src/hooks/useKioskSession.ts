/**
 * Kiosk Session State Management Hook
 * ===================================
 * 
 * File Purpose:
 * -------------
 * Manages active kiosk encounter state across the 5 screen transitions:
 * Active Step, Patient Demographic Profile, Active Session ID, Consent Record,
 * and Doctor Reviewer Context.
 * 
 * Connected to:
 * -------------
 * - `frontend/src/App.tsx`: Drives page switching and state persistence.
 */

import { useState, useCallback } from 'react';
import { PatientData } from '../services/api';

export interface KioskSessionState {
  currentStep: number;
  patient: PatientData | null;
  sessionId: string | null;
  consentGranted: boolean;
  doctorId: string;
}

export const useKioskSession = () => {
  const [sessionState, setSessionState] = useState<KioskSessionState>({
    currentStep: 1, // 1: Identify, 2: Converse, 3: Scan, 4: Summary, 5: Consult
    patient: null,
    sessionId: null,
    consentGranted: false,
    doctorId: 'dr_opd_01'
  });

  const nextStep = useCallback(() => {
    // Step 1: Advance currentStep up to max 5.
    setSessionState((prev) => ({ ...prev, currentStep: Math.min(prev.currentStep + 1, 5) }));
  }, []);

  const goToStep = useCallback((step: number) => {
    // Step 1: Navigate directly to specified step.
    setSessionState((prev) => ({ ...prev, currentStep: step }));
  }, []);

  const resetKiosk = useCallback(() => {
    // Step 1: Reset all patient and session data back to idle initial state.
    setSessionState({
      currentStep: 1,
      patient: null,
      sessionId: null,
      consentGranted: false,
      doctorId: 'dr_opd_01'
    });
  }, []);

  const setPatientData = useCallback((patient: PatientData, consentGranted: boolean) => {
    // Step 1: Save patient profile and consent.
    setSessionState((prev) => ({ ...prev, patient, consentGranted }));
  }, []);

  const setSessionId = useCallback((sessionId: string) => {
    // Step 1: Save created session UUID.
    setSessionState((prev) => ({ ...prev, sessionId }));
  }, []);

  return {
    ...sessionState,
    nextStep,
    goToStep,
    resetKiosk,
    setPatientData,
    setSessionId
  };
};
