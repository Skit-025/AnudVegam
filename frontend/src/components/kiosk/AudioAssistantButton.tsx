/**
 * Audio Assistant Text-to-Speech Button
 * =====================================
 * 
 * Speaks the current question or prompt aloud using the browser's native
 * SpeechSynthesis API to assist elderly or visually impaired patients.
 */

import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

interface AudioAssistantButtonProps {
  textToSpeak: string;
  lang?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const AudioAssistantButton: React.FC<AudioAssistantButtonProps> = ({
  textToSpeak,
  lang = 'en',
  size = 'md'
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  const handleSpeak = () => {
    if (!('speechSynthesis' in window)) return;

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.9; // clear, comfortable pace for patients

    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    setIsPlaying(true);
    window.speechSynthesis.speak(utterance);
  };

  const sizeClasses = {
    sm: 'p-2 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-3 text-base'
  }[size];

  return (
    <button
      onClick={handleSpeak}
      className={`inline-flex items-center space-x-2 rounded-xl border font-medium transition-all ${sizeClasses} ${
        isPlaying
          ? 'bg-clinical-50 border-clinical-500 text-clinical-700 ring-2 ring-clinical-400/30'
          : 'bg-white border-slate-200 text-slate-700 hover:border-clinical-400 hover:text-clinical-700 shadow-sm'
      }`}
      title="Hear question spoken aloud"
    >
      {isPlaying ? (
        <>
          <VolumeX className="w-5 h-5 text-clinical-600 animate-pulse" />
          <span>Stop Audio</span>
        </>
      ) : (
        <>
          <Volume2 className="w-5 h-5 text-clinical-600" />
          <span>Listen to Question</span>
        </>
      )}
    </button>
  );
};
