/**
 * Screen 1: Patient Identification Screen
 * =======================================
 * 
 * Enforces prompt specification §10:
 * Extremely simple, non-intimidating interface.
 * Allows entering 14-digit ABHA number or 1-tap "Continue with Demo Patient".
 * Saves session context into cookies (zero localStorage).
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PatientLayout } from '../../components/layout/PatientLayout';
import { MediKioskApi, PatientData } from '../../services/api';
import { cookieStorage } from '../../utils/cookieStorage';
import { AudioAssistantButton } from '../../components/kiosk/AudioAssistantButton';
import { ArrowRight, UserCheck, CreditCard, Sparkles, Delete } from 'lucide-react';

export const IdentifyPage: React.FC = () => {
  const navigate = useNavigate();
  const [abhaInput, setAbhaInput] = useState('91-1234-5678-9012');
  const [manualName, setManualName] = useState('Ramesh Kumar');
  const [manualAge, setManualAge] = useState(45);
  const [manualGender, setManualGender] = useState('MALE');
  const [isLoading, setIsLoading] = useState(false);
  const [lookupSuccess, setLookupSuccess] = useState(false);

  const handleKeypadPress = (val: string) => {
    let clean = abhaInput.replace(/[^0-9]/g, '');
    if (clean.length >= 14) return;
    clean += val;
    formatAndSetAbha(clean);
  };

  const handleBackspace = () => {
    let clean = abhaInput.replace(/[^0-9]/g, '');
    clean = clean.slice(0, -1);
    formatAndSetAbha(clean);
  };

  const formatAndSetAbha = (digits: string) => {
    let formatted = digits;
    if (digits.length > 2) formatted = digits.slice(0, 2) + '-' + digits.slice(2);
    if (digits.length > 6) formatted = formatted.slice(0, 7) + '-' + digits.slice(6);
    if (digits.length > 10) formatted = formatted.slice(0, 12) + '-' + digits.slice(10, 14);
    setAbhaInput(formatted);
  };

  const handleLookupAndProceed = async () => {
    setIsLoading(true);
    try {
      const patient = await MediKioskApi.lookupAbha(abhaInput);
      setManualName(patient.name);
      setManualAge(patient.age);
      setManualGender(patient.gender);
      setLookupSuccess(true);

      const registered = await MediKioskApi.createOrIdentifyPatient(patient);
      cookieStorage.setJSON('medikiosk_patient', registered);
      setTimeout(() => {
        setIsLoading(false);
        navigate('/consent');
      }, 600);
    } catch {
      const fallbackPatient: PatientData = {
        id: 'p-ramesh-001',
        abha_id: abhaInput || '91-1234-5678-9012',
        name: manualName || 'Ramesh Kumar',
        age: manualAge || 45,
        gender: manualGender || 'MALE',
        preferred_language: cookieStorage.get('medikiosk_language') || 'hi'
      };
      cookieStorage.setJSON('medikiosk_patient', fallbackPatient);
      setIsLoading(false);
      navigate('/consent');
    }
  };

  const handleUseDemoPatient = async (name: string, age: number, gender: string, abha: string, lang: string) => {
    setIsLoading(true);
    const demoPatient: PatientData = {
      id: `p-demo-${Date.now()}`,
      abha_id: abha,
      name,
      age,
      gender,
      preferred_language: lang
    };
    cookieStorage.setJSON('medikiosk_patient', demoPatient);
    cookieStorage.set('medikiosk_language', lang);
    setTimeout(() => {
      setIsLoading(false);
      navigate('/consent');
    }, 400);
  };

  return (
    <PatientLayout currentStep={1} onResetSession={() => navigate('/')}>
      <div className="max-w-2xl mx-auto w-full bg-white rounded-3xl border border-surface-border p-8 md:p-10 shadow-lg space-y-8 animate-fadeIn">
        {/* Step Header */}
        <div className="flex justify-between items-start">
          <div className="space-y-1">
            <span className="text-xs font-bold text-clinical-700 tracking-wider uppercase font-mono">
              Step 1 of 5 • Identification
            </span>
            <h2 className="text-3xl font-extrabold text-navy-950">Let's find your medical record</h2>
            <p className="text-sm text-text-secondary">Enter your 14-digit ABHA number or tap a demo profile below</p>
          </div>

          <AudioAssistantButton
            textToSpeak="Please enter your 14 digit ABHA health ID, or tap Continue with Demo Patient."
            size="sm"
          />
        </div>

        {/* 14-Digit ABHA Input Field */}
        <div className="space-y-3">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
            <CreditCard className="w-4 h-4 text-clinical-600" />
            <span>ABHA Health ID Number (आभा संख्या)</span>
          </label>
          <div className="relative">
            <input
              type="text"
              value={abhaInput}
              onChange={(e) => setAbhaInput(e.target.value)}
              placeholder="91-XXXX-XXXX-XXXX"
              className="w-full h-16 px-5 text-2xl font-mono tracking-widest text-center font-bold text-navy-950 bg-slate-50 border-2 border-slate-300 rounded-2xl focus:border-clinical-600 focus:bg-white focus:outline-none transition shadow-inner"
            />
          </div>
        </div>

        {/* On-Screen Kiosk Touch Numeric Keypad */}
        <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block text-center">
            Touch Keypad (कियोस्क टच कीपैड)
          </span>
          <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto">
            {['1', '2', '3', '4', '5', '6', '7', '8', '9'].map((digit) => (
              <button
                key={digit}
                type="button"
                onClick={() => handleKeypadPress(digit)}
                className="h-12 bg-white hover:bg-clinical-50 text-navy-950 font-bold text-xl rounded-xl border border-slate-200 hover:border-clinical-400 active:scale-95 transition shadow-sm"
              >
                {digit}
              </button>
            ))}
            <button
              type="button"
              onClick={() => setAbhaInput('')}
              className="h-12 bg-white hover:bg-red-50 text-red-600 font-semibold text-xs rounded-xl border border-slate-200 hover:border-red-300 active:scale-95 transition"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={() => handleKeypadPress('0')}
              className="h-12 bg-white hover:bg-clinical-50 text-navy-950 font-bold text-xl rounded-xl border border-slate-200 hover:border-clinical-400 active:scale-95 transition shadow-sm"
            >
              0
            </button>
            <button
              type="button"
              onClick={handleBackspace}
              className="h-12 bg-white hover:bg-amber-50 text-slate-700 font-bold rounded-xl border border-slate-200 hover:border-amber-300 flex items-center justify-center active:scale-95 transition"
              title="Delete"
            >
              <Delete className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Continue Action Button */}
        <button
          onClick={handleLookupAndProceed}
          disabled={isLoading}
          className="w-full h-16 bg-clinical-600 hover:bg-clinical-700 text-white rounded-2xl font-extrabold text-xl flex items-center justify-center space-x-3 shadow-lg shadow-clinical-600/25 transition active:scale-95 kiosk-touch-btn"
        >
          <span>{isLoading ? 'Verifying ABHA ID...' : 'Continue / आगे बढ़ें'}</span>
          <ArrowRight className="w-6 h-6" />
        </button>

        {/* Quick Demo Patients Selection */}
        <div className="pt-2 border-t border-slate-200 space-y-3">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block text-center">
            Or Quick 1-Tap Demo Patient Profiles
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleUseDemoPatient('Ramesh Kumar', 45, 'MALE', '91-1234-5678-9012', 'hi')}
              className="p-3 bg-slate-50 hover:bg-clinical-50 border border-slate-200 hover:border-clinical-400 rounded-xl text-left transition flex items-center space-x-3 group"
            >
              <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-xs">
                RK
              </span>
              <div>
                <span className="font-bold text-sm text-navy-900 block group-hover:text-clinical-700">
                  Ramesh Kumar (45y, Male)
                </span>
                <span className="text-[11px] text-text-secondary block">Hindi • General Fever & Chronic BP</span>
              </div>
            </button>

            <button
              type="button"
              onClick={() => handleUseDemoPatient('Sunita Devi', 58, 'FEMALE', '91-9876-5432-1098', 'en')}
              className="p-3 bg-slate-50 hover:bg-clinical-50 border border-slate-200 hover:border-clinical-400 rounded-xl text-left transition flex items-center space-x-3 group"
            >
              <span className="w-8 h-8 rounded-full bg-red-100 text-red-700 font-bold flex items-center justify-center text-xs">
                SD
              </span>
              <div>
                <span className="font-bold text-sm text-navy-900 block group-hover:text-clinical-700">
                  Sunita Devi (58y, Female)
                </span>
                <span className="text-[11px] text-text-secondary block">English • Acute Chest Pain Scenario</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </PatientLayout>
  );
};
