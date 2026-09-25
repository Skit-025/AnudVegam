/**
 * Screen 0: Welcome & Landing Screen
 * ==================================
 * 
 * Enforces prompt specification §8:
 * Communicates: "Your medical history, ready before consultation."
 * Features calm ambient clinical waveform, language selection, audio assistance, and instant start.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Globe, Volume2, Shield, HeartPulse, Sparkles, UserCheck } from 'lucide-react';
import { LanguageModal, SUPPORTED_LANGUAGES } from '../components/kiosk/LanguageModal';
import { cookieStorage } from '../utils/cookieStorage';

export const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const [isLangOpen, setIsLangOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState(() => cookieStorage.get('medikiosk_language') || 'en');
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);

  const activeLangObj = SUPPORTED_LANGUAGES.find(l => l.code === currentLang) || SUPPORTED_LANGUAGES[0];

  const handleStart = () => {
    navigate('/identify');
  };

  const handlePlayInstructions = () => {
    if (!('speechSynthesis' in window)) return;
    if (isAudioPlaying) {
      window.speechSynthesis.cancel();
      setIsAudioPlaying(false);
      return;
    }
    window.speechSynthesis.cancel();
    const text = activeLangObj.code === 'hi'
      ? 'मेडीकियोस्क में आपका स्वागत है। डॉक्टर से मिलने से पहले अपने लक्षण और पर्चियां यहां दर्ज करें। शुरू करने के लिए नीचे दिए गए बटन को दबाएं।'
      : 'Welcome to MediKiosk. Please record your health history and scan your prescriptions before meeting your doctor. Tap Start to begin.';
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = activeLangObj.code === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.onend = () => setIsAudioPlaying(false);
    setIsAudioPlaying(true);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between font-sans text-navy-950 select-none">
      {/* Top Welcome Header */}
      <header className="px-8 py-6 max-w-7xl w-full mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-2xl bg-clinical-600 text-white flex items-center justify-center font-bold text-2xl shadow-lg shadow-clinical-600/20">
            🏥
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-navy-900">MEDIKIOSK</h1>
            <p className="text-xs text-clinical-700 font-medium">Digital OPD Clinical Intake System</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/demo')}
            className="px-4 py-2 rounded-xl bg-purple-50 text-purple-700 border border-purple-200 font-bold text-xs flex items-center space-x-1.5 hover:bg-purple-100 transition shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
            <span>Judge Demo Scenarios</span>
          </button>

          <button
            onClick={() => navigate('/doctor')}
            className="px-4 py-2 rounded-xl bg-navy-900 text-white font-bold text-xs hover:bg-navy-800 transition flex items-center space-x-1.5 shadow-sm"
          >
            <UserCheck className="w-3.5 h-3.5 text-clinical-400" />
            <span>Doctor View</span>
          </button>
        </div>
      </header>

      {/* Hero Welcome Center */}
      <main className="max-w-4xl w-full mx-auto px-6 py-12 flex flex-col items-center text-center space-y-8">
        {/* Ambient Medical Pulse Waveform */}
        <div className="flex items-center space-x-2 h-10 px-6 py-2 rounded-full bg-clinical-50 border border-clinical-200 shadow-inner">
          <HeartPulse className="w-5 h-5 text-clinical-600 animate-pulse" />
          <div className="flex items-center space-x-1 h-5">
            {[20, 50, 90, 30, 80, 100, 45, 70, 25].map((h, idx) => (
              <div
                key={idx}
                style={{ height: `${h}%`, animationDelay: `${idx * 0.15}s` }}
                className="w-1 bg-clinical-500 rounded-full animate-wave-pulse"
              />
            ))}
          </div>
          <span className="text-xs font-bold text-clinical-800 font-mono tracking-wider ml-2">
            OPD TRIAGE KIOSK ACTIVE
          </span>
        </div>

        {/* Hero Title */}
        <div className="space-y-4">
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-navy-950 tracking-tight leading-tight">
            Your medical history, <br />
            <span className="text-clinical-600">ready before consultation.</span>
          </h2>
          <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto font-normal leading-relaxed">
            Answer a few quick questions using your voice or touch, and scan your past prescriptions.
            Your doctor will have your complete case summary ready when you enter.
          </p>
        </div>

        {/* Primary Action Button */}
        <div className="w-full max-w-md space-y-4">
          <button
            onClick={handleStart}
            className="w-full h-16 bg-clinical-600 hover:bg-clinical-700 text-white rounded-2xl font-extrabold text-xl flex items-center justify-center space-x-3 shadow-xl shadow-clinical-600/25 transition-all transform active:scale-95 kiosk-touch-btn"
          >
            <span>Touch to Start / शुरू करें</span>
            <ArrowRight className="w-6 h-6" />
          </button>

          {/* Language & Audio Pill Buttons */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <button
              onClick={() => setIsLangOpen(true)}
              className="h-12 bg-white hover:bg-slate-50 border-2 border-slate-200 text-navy-900 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition shadow-sm"
            >
              <Globe className="w-4 h-4 text-clinical-600" />
              <span>{activeLangObj.native} ({activeLangObj.english})</span>
            </button>

            <button
              onClick={handlePlayInstructions}
              className={`h-12 border-2 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition shadow-sm ${
                isAudioPlaying
                  ? 'bg-clinical-50 border-clinical-500 text-clinical-700 ring-2 ring-clinical-400/30'
                  : 'bg-white hover:bg-slate-50 border-slate-200 text-navy-900'
              }`}
            >
              <Volume2 className={`w-4 h-4 ${isAudioPlaying ? 'text-clinical-600 animate-bounce' : 'text-slate-600'}`} />
              <span>{isAudioPlaying ? 'Playing Audio...' : 'Hear Audio Help'}</span>
            </button>
          </div>
        </div>

        {/* Three Value Pillars */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full pt-8 text-left">
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-start space-x-3">
            <span className="p-2 rounded-xl bg-blue-50 text-blue-600 font-bold text-lg">🗣️</span>
            <div>
              <h4 className="font-bold text-sm text-navy-900">Voice or Touch</h4>
              <p className="text-xs text-text-secondary mt-0.5">Simply speak your symptoms in your own native language.</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-start space-x-3">
            <span className="p-2 rounded-xl bg-purple-50 text-purple-600 font-bold text-lg">📄</span>
            <div>
              <h4 className="font-bold text-sm text-navy-900">Instant OCR Scan</h4>
              <p className="text-xs text-text-secondary mt-0.5">Place paper prescriptions under the camera to digitize medicines.</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-start space-x-3">
            <span className="p-2 rounded-xl bg-emerald-50 text-emerald-600 font-bold text-lg">🩺</span>
            <div>
              <h4 className="font-bold text-sm text-navy-900">Doctor-Reviewed</h4>
              <p className="text-xs text-text-secondary mt-0.5">Your attending physician reviews and verifies all case notes.</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Disclaimer */}
      <footer className="px-8 py-4 border-t border-slate-200 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between max-w-7xl w-full mx-auto">
        <span className="flex items-center space-x-1.5">
          <Shield className="w-3.5 h-3.5 text-clinical-600" />
          <span>Compliant with Ayushman Bharat Digital Mission (ABDM) & HL7 FHIR R4 Standards.</span>
        </span>
        <span className="mt-1 sm:mt-0 font-medium text-slate-400">SIH26047 Prototype • Smart India Hackathon</span>
      </footer>

      {/* Language Modal */}
      <LanguageModal
        isOpen={isLangOpen}
        onClose={() => setIsLangOpen(false)}
        selectedLanguage={currentLang}
        onSelectLanguage={(code) => setCurrentLang(code)}
      />
    </div>
  );
};
