/**
 * Voice Interaction Waveform & State Indicator
 * ============================================
 * 
 * Visualizes the 5 audio interaction states:
 * - Idle
 * - Listening (smooth responsive audio wave bars)
 * - Understanding (subtle pulsing state)
 * - Got it ✓ (clear confirmation)
 */

import React from 'react';
import { Mic, Check, Loader2 } from 'lucide-react';

export type VoiceState = 'idle' | 'listening' | 'understanding' | 'understood';

interface VoiceWaveformProps {
  state: VoiceState;
  onToggleRecord?: () => void;
  transcript?: string;
}

export const VoiceWaveform: React.FC<VoiceWaveformProps> = ({
  state,
  onToggleRecord,
  transcript
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-6 space-y-4">
      {/* Central Visual Indicator Button */}
      <div className="relative flex items-center justify-center">
        {state === 'listening' && (
          <>
            <div className="absolute w-24 h-24 rounded-full bg-clinical-500/20 animate-ping" />
            <div className="absolute w-20 h-20 rounded-full bg-clinical-500/30 animate-pulse" />
          </>
        )}

        <button
          onClick={onToggleRecord}
          className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg ${
            state === 'listening'
              ? 'bg-clinical-600 text-white ring-4 ring-clinical-300 scale-105'
              : state === 'understanding'
              ? 'bg-amber-500 text-white animate-spin'
              : state === 'understood'
              ? 'bg-emerald-600 text-white'
              : 'bg-white border-2 border-slate-300 text-slate-700 hover:border-clinical-500 hover:text-clinical-600'
          }`}
          title="Voice input"
        >
          {state === 'listening' && <Mic className="w-8 h-8 animate-bounce" />}
          {state === 'understanding' && <Loader2 className="w-8 h-8" />}
          {state === 'understood' && <Check className="w-8 h-8" />}
          {state === 'idle' && <Mic className="w-8 h-8" />}
        </button>
      </div>

      {/* State Text Feedback */}
      <div className="text-center">
        {state === 'listening' && (
          <div className="space-y-2">
            <span className="inline-flex items-center space-x-2 text-clinical-700 font-semibold text-lg tracking-wide">
              <span className="w-2.5 h-2.5 rounded-full bg-clinical-600 animate-pulse" />
              <span>Listening... Speak now</span>
            </span>
            {/* Animated waveform bars */}
            <div className="flex items-center justify-center space-x-1.5 h-8">
              {[40, 75, 100, 60, 90, 45, 80, 50, 70, 30].map((height, i) => (
                <div
                  key={i}
                  style={{
                    height: `${height}%`,
                    animationDelay: `${i * 0.1}s`,
                    animationDuration: '1.2s'
                  }}
                  className="w-1.5 bg-clinical-500 rounded-full animate-wave-pulse"
                />
              ))}
            </div>
          </div>
        )}

        {state === 'understanding' && (
          <span className="text-amber-700 font-semibold text-base flex items-center space-x-2">
            <span>Understanding your answer...</span>
          </span>
        )}

        {state === 'understood' && (
          <span className="text-emerald-700 font-semibold text-base flex items-center space-x-2">
            <span>Got it ✓</span>
          </span>
        )}

        {state === 'idle' && (
          <span className="text-text-secondary text-sm">
            Tap microphone to speak, or select an option below
          </span>
        )}
      </div>

      {/* Real-time transcribed text display */}
      {transcript && transcript.trim() && (
        <div className="w-full max-w-lg bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-center text-navy-900 font-medium text-base shadow-inner">
          "{transcript}"
        </div>
      )}
    </div>
  );
};
