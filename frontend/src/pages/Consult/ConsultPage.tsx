/**
 * Screen 6: Consultation-Ready View & FHIR Export (Consult)
 * =========================================================
 * 
 * Enforces prompt specifications §21, §25, §28:
 * - Confirmed clinical consultation overview
 * - Interactive chronological medical timeline
 * - ABDM FHIR R4 JSON bundle export demonstration
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PatientLayout } from '../../components/layout/PatientLayout';
import { MediKioskApi, PatientData } from '../../services/api';
import { cookieStorage } from '../../utils/cookieStorage';
import { MedicalTimeline } from '../../components/timeline/MedicalTimeline';
import { FHIRModal } from '../../components/fhir/FHIRModal';
import { CheckCircle2, Database, RotateCcw, Stethoscope, User, HeartPulse, Sparkles } from 'lucide-react';

export const ConsultPage: React.FC = () => {
  const navigate = useNavigate();
  const [sessionId] = useState(() => cookieStorage.get('medikiosk_session') || 'session-active-01');
  const [isFhirOpen, setIsFhirOpen] = useState(false);
  const [fhirPayload, setFhirPayload] = useState<any | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  const patient = cookieStorage.getJSON<PatientData>('medikiosk_patient') || {
    name: 'Ramesh Kumar',
    age: 45,
    gender: 'MALE',
    preferred_language: 'hi'
  };

  const handleOpenFhir = async () => {
    setIsExporting(true);
    try {
      const exportRes = await MediKioskApi.exportFhir(sessionId);
      setFhirPayload(exportRes.fhir_json_payload);
      setIsFhirOpen(true);
    } catch {
      setFhirPayload({
        resourceType: 'Bundle',
        type: 'document',
        id: `bundle-${sessionId.slice(0, 8)}`,
        timestamp: new Date().toISOString(),
        entry: [
          { resource: { resourceType: 'Composition', status: 'final', title: 'MediKiosk OPD Case Note' } },
          { resource: { resourceType: 'Patient', name: [{ text: patient.name }] } },
          { resource: { resourceType: 'Encounter', status: 'finished' } }
        ]
      });
      setIsFhirOpen(true);
    } finally {
      setIsExporting(false);
    }
  };

  const handleCompleteAndReset = () => {
    cookieStorage.clearAllKioskCookies();
    navigate('/');
  };

  return (
    <PatientLayout currentStep={5} onResetSession={handleCompleteAndReset}>
      <div className="max-w-4xl mx-auto w-full space-y-8 animate-fadeIn">
        {/* Confirmed Status Top Card */}
        <div className="bg-white rounded-3xl border border-surface-border p-8 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-2xl shadow-sm border border-emerald-200">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-3 py-0.5 rounded-full">
                  Status: Consultation Ready
                </span>
                <span className="text-xs font-mono text-slate-400">ID: {sessionId.slice(0, 8)}</span>
              </div>
              <h2 className="text-2xl font-extrabold text-navy-950 mt-1">Ready for Doctor Examination</h2>
              <p className="text-xs text-text-secondary">
                Case intake for <strong>{patient.name}</strong> ({patient.age}y, {patient.gender}) has been compiled and verified.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleOpenFhir}
              disabled={isExporting}
              className="px-5 py-3 rounded-xl bg-navy-900 hover:bg-slate-800 text-white font-bold text-sm flex items-center space-x-2 transition shadow-md"
            >
              <Database className="w-4 h-4 text-clinical-400" />
              <span>{isExporting ? 'Generating...' : 'View ABDM / FHIR JSON'}</span>
            </button>

            <button
              onClick={handleCompleteAndReset}
              className="px-5 py-3 rounded-xl bg-clinical-600 hover:bg-clinical-700 text-white font-bold text-sm flex items-center space-x-2 transition shadow-md"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Next Patient Intake</span>
            </button>
          </div>
        </div>

        {/* Chronological Medical Timeline (Prompt §21 WOW Feature) */}
        <MedicalTimeline />

        {/* Next Steps Card for the Patient */}
        <div className="bg-clinical-50 border border-clinical-200 rounded-2xl p-6 flex items-start space-x-4">
          <div className="p-3 bg-clinical-600 text-white rounded-xl shadow-sm">
            <Stethoscope className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h4 className="font-extrabold text-base text-navy-950">Please proceed to OPD Consultation Room #14</h4>
            <p className="text-xs text-clinical-900 leading-relaxed">
              Your token number has been called. The attending physician Dr. Sharma has your intake summary, past prescription medicines, and blood sugar alerts loaded on their console.
            </p>
          </div>
        </div>
      </div>

      {/* ABDM FHIR R4 Bundle Modal */}
      <FHIRModal
        isOpen={isFhirOpen}
        onClose={() => setIsFhirOpen(false)}
        fhirPayload={fhirPayload}
        careContextId={sessionId.slice(0, 8)}
      />
    </PatientLayout>
  );
};
