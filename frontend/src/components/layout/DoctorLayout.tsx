/**
 * Doctor OPD Consultation Master Layout
 * =====================================
 * 
 * High-density clinical dashboard for OPD physicians:
 * - Patient Banner with ABHA ID, Age, Gender, Language, and Live Triage Status
 * - Clinical Tab Bar: Overview | Timeline | History Q&A | Documents & OCR | AI Summary | ABDM FHIR
 * - Red-Flag Emergency Triage Indicators
 */

import React from 'react';
import { User, Activity, FileText, Sparkles, Database, Stethoscope, AlertTriangle, ArrowLeft } from 'lucide-react';
import { PatientData } from '../../services/api';

export type DoctorTab = 'overview' | 'timeline' | 'history' | 'documents' | 'summary' | 'fhir';

interface DoctorLayoutProps {
  patient: PatientData | null;
  activeTab: DoctorTab;
  onTabChange: (tab: DoctorTab) => void;
  hasRedFlag?: boolean;
  redFlagReason?: string | null;
  onBackToKiosk?: () => void;
  children: React.ReactNode;
}

export const DoctorLayout: React.FC<DoctorLayoutProps> = ({
  patient,
  activeTab,
  onTabChange,
  hasRedFlag = false,
  redFlagReason,
  onBackToKiosk,
  children
}) => {
  const tabs = [
    { id: 'overview' as DoctorTab, label: 'Clinical Snapshot', icon: Stethoscope },
    { id: 'timeline' as DoctorTab, label: 'Medical Timeline', icon: Activity },
    { id: 'history' as DoctorTab, label: 'Interview Q&A', icon: User },
    { id: 'documents' as DoctorTab, label: 'Scanned Records & OCR', icon: FileText },
    { id: 'summary' as DoctorTab, label: 'AI Summary & Editor', icon: Sparkles },
    { id: 'fhir' as DoctorTab, label: 'ABDM / FHIR R4', icon: Database },
  ];

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Doctor Navigation */}
      <header className="bg-navy-900 text-white border-b border-slate-800 px-6 py-3 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {onBackToKiosk && (
              <button
                onClick={onBackToKiosk}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                title="Return to Kiosk Intake"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
            )}
            <div className="w-8 h-8 rounded-lg bg-clinical-600 flex items-center justify-center font-bold text-white text-sm">
              Dr
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-tight">OPD Physician Console</h2>
              <p className="text-xs text-slate-400">Dr. Sharma, MD (Internal Medicine) • Room #14</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1 rounded-full flex items-center space-x-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>LIVE Consultation Mode</span>
            </span>
          </div>
        </div>
      </header>

      {/* Patient Clinical Banner */}
      <div className="bg-white border-b border-surface-border py-4 px-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-clinical-100 text-clinical-700 flex items-center justify-center font-bold text-lg border border-clinical-200 shadow-sm">
              {patient?.name ? patient.name[0].toUpperCase() : 'P'}
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h3 className="text-xl font-bold text-navy-950">{patient?.name || 'Demo Patient'}</h3>
                <span className="text-xs bg-slate-100 text-slate-700 font-mono px-2.5 py-0.5 rounded border">
                  ABHA: {patient?.abha_id || '91-1234-5678-9012'}
                </span>
                {hasRedFlag && (
                  <span className="text-xs bg-red-100 text-red-800 font-bold px-3 py-0.5 rounded-full flex items-center space-x-1 border border-red-200">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>PRIORITY RED-FLAG</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-text-secondary mt-0.5">
                Age: <span className="font-semibold text-slate-800">{patient?.age || 45} yrs</span> •
                Gender: <span className="font-semibold text-slate-800">{patient?.gender || 'MALE'}</span> •
                Language: <span className="font-semibold text-slate-800">{patient?.preferred_language?.toUpperCase() || 'HI'}</span> •
                Phone: <span className="font-semibold text-slate-800">{patient?.phone || '9876543210'}</span>
              </p>
            </div>
          </div>

          {/* Red Flag Quick Alert Bar */}
          {hasRedFlag && redFlagReason && (
            <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-2 text-xs text-red-900 max-w-md">
              <span className="font-bold block text-red-700 uppercase">Attention Required:</span>
              <span>{redFlagReason}</span>
            </div>
          )}
        </div>
      </div>

      {/* Doctor Tabs Navigation */}
      <div className="bg-white border-b border-surface-border px-6 sticky top-[57px] z-30 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center space-x-1 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`py-3.5 px-4 font-semibold text-sm flex items-center space-x-2 border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-clinical-600 text-clinical-700 bg-clinical-50/40'
                    : 'border-transparent text-slate-600 hover:text-navy-900 hover:border-slate-300'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-clinical-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Tab View */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-6">
        {children}
      </main>
    </div>
  );
};
