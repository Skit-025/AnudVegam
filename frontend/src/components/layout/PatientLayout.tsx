/**
 * Patient Kiosk Master Layout
 * ===========================
 * 
 * Provides the hospital kiosk framing:
 * - OPD Hospital Title & Live Clock
 * - Language switcher pill & Audio assistant
 * - Emergency nurse call trigger
 * - Persistent 5-step patient progress track
 */

import React, { useState, useEffect } from 'react';
import { Globe, Volume2, PhoneCall, AlertTriangle, ShieldCheck } from 'lucide-react';
import { LanguageModal, SUPPORTED_LANGUAGES } from '../kiosk/LanguageModal';
import { cookieStorage } from '../../utils/cookieStorage';

interface PatientLayoutProps {
  currentStep: number; // 1: Identify, 2: Consent, 3: History, 4: Documents, 5: Summary
  children: React.ReactNode;
  onResetSession?: () => void;
}

const STEP_LABELS = [
  { step: 1, label: 'Identity', native: 'पहचान' },
  { step: 2, label: 'Consent', native: 'सहमति' },
  { step: 3, label: 'History', native: 'लक्षण' },
  { step: 4, label: 'Documents', native: 'कागज़ात' },
  { step: 5, label: 'Summary', native: 'सारांश' }
];

export const PatientLayout: React.FC<PatientLayoutProps> = ({
  currentStep,
  children,
  onResetSession
}) => {
  const [timeStr, setTimeStr] = useState('');
  const [isLangOpen, setIsLangOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState('en');
  const [nurseAlertSent, setNurseAlertSent] = useState(false);

  useEffect(() => {
    // Clock updater
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    // Initial language from cookie
    const savedLang = cookieStorage.get('medikiosk_language') || 'en';
    setCurrentLang(savedLang);

    return () => clearInterval(interval);
  }, []);

  const activeLangObj = SUPPORTED_LANGUAGES.find(l => l.code === currentLang) || SUPPORTED_LANGUAGES[0];

  const handleCallNurse = () => {
    setNurseAlertSent(true);
    setTimeout(() => setNurseAlertSent(false), 4000);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans select-none">
      {/* Top Clinical Kiosk Header */}
      <header className="bg-navy-950 text-white px-6 py-4 shadow-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Hospital Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-clinical-600 flex items-center justify-center font-bold text-white shadow-md">
              <span className="text-xl">🏥</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="font-extrabold text-lg tracking-wide text-white">MEDIKIOSK</h1>
                <span className="text-[10px] bg-clinical-500/20 text-clinical-300 px-2 py-0.5 rounded font-mono uppercase tracking-wider">
                  OPD Intake
                </span>
              </div>
              <p className="text-xs text-slate-400">All India Institute of Medical Sciences (AIIMS) / Civil Hospital</p>
            </div>
          </div>

          {/* Quick Controls */}
          <div className="flex items-center space-x-3">
            {/* Live Clock */}
            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-navy-900 text-slate-300 text-xs font-mono border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>{timeStr}</span>
            </div>

            {/* Language Selector Button */}
            <button
              onClick={() => setIsLangOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-navy-900 hover:bg-slate-800 border border-slate-800 text-white text-xs font-medium flex items-center space-x-2 transition"
              title="Change Language"
            >
              <Globe className="w-4 h-4 text-clinical-400" />
              <span className="font-semibold">{activeLangObj.native}</span>
              <span className="text-slate-400">({activeLangObj.english})</span>
            </button>

            {/* Emergency Staff Call Button */}
            <button
              onClick={handleCallNurse}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition ${
                nurseAlertSent
                  ? 'bg-amber-500 text-white shadow-lg animate-pulse'
                  : 'bg-red-950/60 hover:bg-red-900/80 border border-red-800/80 text-red-200'
              }`}
            >
              <PhoneCall className="w-3.5 h-3.5" />
              <span>{nurseAlertSent ? 'Staff Notified' : 'Need Help'}</span>
            </button>

            {/* Reset / Exit */}
            {onResetSession && (
              <button
                onClick={onResetSession}
                className="text-xs text-slate-400 hover:text-white px-2 py-1 transition"
                title="Cancel & Reset Kiosk"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Persistent 5-Step Guided Progress Tracker */}
      <div className="bg-white border-b border-surface-border py-3 px-6 shadow-sm sticky top-[68px] z-30">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {STEP_LABELS.map((item, idx) => {
            const isCompleted = item.step < currentStep;
            const isCurrent = item.step === currentStep;

            return (
              <React.Fragment key={item.step}>
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                      isCompleted
                        ? 'bg-clinical-600 text-white shadow'
                        : isCurrent
                        ? 'bg-navy-950 text-white ring-4 ring-clinical-500/20 scale-110 shadow-md'
                        : 'bg-slate-100 text-slate-400 border border-slate-200'
                    }`}
                  >
                    {isCompleted ? '✓' : item.step}
                  </div>
                  <div className="hidden sm:block">
                    <span
                      className={`text-xs font-bold block ${
                        isCurrent ? 'text-navy-950' : isCompleted ? 'text-clinical-800' : 'text-slate-400'
                      }`}
                    >
                      {item.label}
                    </span>
                    <span className="text-[10px] text-slate-400 font-medium block leading-none">
                      {item.native}
                    </span>
                  </div>
                </div>

                {idx < STEP_LABELS.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-3 transition-colors ${
                      item.step < currentStep ? 'bg-clinical-600' : 'bg-slate-200'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Main Kiosk Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 flex flex-col justify-center">
        {children}
      </main>

      {/* Language Selection Modal */}
      <LanguageModal
        isOpen={isLangOpen}
        onClose={() => setIsLangOpen(false)}
        selectedLanguage={currentLang}
        onSelectLanguage={(code) => setCurrentLang(code)}
      />
    </div>
  );
};
