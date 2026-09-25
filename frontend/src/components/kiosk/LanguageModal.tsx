/**
 * Language Selection Modal Component
 * ==================================
 * 
 * Provides high-accessibility language cards with native scripts, English labels,
 * and audio preview assistance for Indian OPD patients.
 */

import React from 'react';
import { Volume2, Check, X } from 'lucide-react';
import { cookieStorage } from '../../utils/cookieStorage';

export interface LanguageOption {
  code: string;
  native: string;
  english: string;
  greeting: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'hi', native: 'हिन्दी', english: 'Hindi', greeting: 'नमस्ते, मेडीकियोस्क में आपका स्वागत है।' },
  { code: 'en', native: 'English', english: 'English', greeting: 'Welcome to MediKiosk.' },
  { code: 'or', native: 'ଓଡ଼ିଆ', english: 'Odia', greeting: 'ମେଡିକିଓସ୍କକୁ ସ୍ୱାଗତ।' },
  { code: 'mr', native: 'मराठी', english: 'Marathi', greeting: 'मेडीकियोस्कमध्ये आपले स्वागत आहे.' },
  { code: 'bn', native: 'বাংলা', english: 'Bengali', greeting: 'মেডিকিয়স্কে আপনাকে স্বাগতম।' },
  { code: 'ta', native: 'தமிழ்', english: 'Tamil', greeting: 'மெடிகியோஸ்கிற்கு நல்வரவு.' },
  { code: 'te', native: 'తెలుగు', english: 'Telugu', greeting: 'మెడికియోస్క్‌కు స్వాగతం.' },
  { code: 'gu', native: 'ગુજરાતી', english: 'Gujarati', greeting: 'મેડીકિયોસ્કમાં આપનું સ્વાગત છે.' }
];

interface LanguageModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedLanguage: string;
  onSelectLanguage: (code: string) => void;
}

export const LanguageModal: React.FC<LanguageModalProps> = ({
  isOpen,
  onClose,
  selectedLanguage,
  onSelectLanguage
}) => {
  if (!isOpen) return null;

  const handlePreviewAudio = (e: React.MouseEvent, lang: LanguageOption) => {
    e.stopPropagation();
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(lang.greeting);
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSelect = (code: string) => {
    cookieStorage.set('medikiosk_language', code);
    onSelectLanguage(code);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-navy-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-6 animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-3xl w-full p-8 shadow-2xl border border-surface-border space-y-6">
        <div className="flex justify-between items-center border-b border-surface-border pb-4">
          <div>
            <h2 className="text-2xl font-bold text-navy-900">Choose Language / भाषा चुनें</h2>
            <p className="text-sm text-text-secondary">Select your preferred language for voice and touch intake</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-surface-subtle text-slate-500 hover:text-navy-900 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = selectedLanguage === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => handleSelect(lang.code)}
                className={`p-5 rounded-2xl text-left border-2 transition-all flex flex-col justify-between h-36 group relative ${
                  isSelected
                    ? 'border-clinical-600 bg-clinical-50/50 shadow-md ring-2 ring-clinical-500/20'
                    : 'border-surface-border hover:border-clinical-300 hover:bg-slate-50'
                }`}
              >
                {isSelected && (
                  <span className="absolute top-3 right-3 bg-clinical-600 text-white rounded-full p-1">
                    <Check className="w-3.5 h-3.5" />
                  </span>
                )}

                <div>
                  <span className="text-2xl font-bold text-navy-900 block font-serif tracking-tight">
                    {lang.native}
                  </span>
                  <span className="text-sm font-medium text-text-secondary">
                    {lang.english}
                  </span>
                </div>

                <div className="flex justify-between items-center pt-2">
                  <span className="text-xs text-clinical-700 font-medium">Select</span>
                  <button
                    onClick={(e) => handlePreviewAudio(e, lang)}
                    title="Audio sample"
                    className="p-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 hover:text-clinical-600 hover:border-clinical-300 transition"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                </div>
              </button>
            );
          })}
        </div>

        <div className="bg-slate-50 p-4 rounded-xl flex items-center justify-between text-xs text-text-secondary">
          <span>🔊 You can switch language or request voice assistance anytime.</span>
          <button onClick={onClose} className="font-semibold text-clinical-600 hover:underline">
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
