/**
 * Screen 3: Adaptive Medical History-Taking (Converse) — The HERO Screen
 * =====================================================================
 * 
 * Enforces prompt specifications §12, §13, §14, §15, §16, §17:
 * - Central question dominates the viewport (32–44px)
 * - Voice-first waveform interaction with clear feedback states
 * - Large touch targets (20–28px) as immediate fallback
 * - Real-time clinical red-flag alert handling
 * - Clean progress tracking without anxiety
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PatientLayout } from '../../components/layout/PatientLayout';
import { MediKioskApi, NextQuestionResponse } from '../../services/api';
import { cookieStorage } from '../../utils/cookieStorage';
import { VoiceWaveform, VoiceState } from '../../components/kiosk/VoiceWaveform';
import { AudioAssistantButton } from '../../components/kiosk/AudioAssistantButton';
import { RedFlagAlertBanner } from '../../components/kiosk/RedFlagAlertBanner';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { ArrowRight, CheckCircle2, MessageSquare, Send } from 'lucide-react';

export const ConversePage: React.FC = () => {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(() => cookieStorage.get('medikiosk_session') || 'session-active-01');
  const [currentQuestion, setCurrentQuestion] = useState<NextQuestionResponse | null>(null);
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [textAnswer, setTextAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [historyTurns, setHistoryTurns] = useState<Array<{ q: string; a: string; isRedFlag?: boolean }>>([]);
  const [activeRedFlag, setActiveRedFlag] = useState<{ detected: boolean; reason?: string | null } | null>(null);

  const { isListening, transcript, startListening, stopListening, resetTranscript } = useSpeechRecognition();

  // Load question on initial mount or step advance
  const fetchNextQuestion = async (sid: string) => {
    try {
      const q = await MediKioskApi.getNextQuestion(sid);
      setCurrentQuestion(q);

      if (q.red_flag?.detected) {
        setActiveRedFlag({
          detected: true,
          reason: q.red_flag.reason
        });
      }

      if (q.is_final) {
        // Automatically proceed to document scanner
        setTimeout(() => {
          navigate('/scan');
        }, 1200);
      }
    } catch {
      // Fallback first question
      setCurrentQuestion({
        question_key: 'chief_complaint',
        question_text: 'What is your main health concern or reason for visiting the OPD today?',
        input_type: 'FREE_TEXT_OR_VOICE',
        options: ['Chest Pain / Discomfort', 'Fever / Chills', 'Cough / Breathlessness', 'Severe Stomach Pain', 'Joint Pain / Body Ache'],
        is_final: false,
        red_flag: { detected: false }
      });
    }
  };

  useEffect(() => {
    const sid = cookieStorage.get('medikiosk_session') || 'session-active-01';
    setSessionId(sid);
    fetchNextQuestion(sid);
  }, []);

  // Sync speech recognition transcript with voice state
  useEffect(() => {
    if (isListening) {
      setVoiceState('listening');
      if (transcript) {
        setTextAnswer(transcript);
      }
    } else if (voiceState === 'listening' && transcript) {
      setVoiceState('understanding');
      setTimeout(() => {
        setVoiceState('understood');
      }, 500);
    }
  }, [isListening, transcript]);

  const handleToggleVoice = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      setTextAnswer('');
      const lang = cookieStorage.get('medikiosk_language') === 'hi' ? 'hi-IN' : 'en-IN';
      startListening(lang);
    }
  };

  const submitAnswer = async (answer: string) => {
    if (!answer.trim() || !currentQuestion || isSubmitting) return;
    setIsSubmitting(true);
    setVoiceState('understanding');

    try {
      const resp = await MediKioskApi.submitAnswer(
        sessionId,
        currentQuestion.question_key,
        currentQuestion.question_text,
        answer,
        voiceState === 'understood' ? 'VOICE' : 'TOUCH'
      );

      // Record in local history transcript
      setHistoryTurns(prev => [
        ...prev,
        {
          q: currentQuestion.question_text,
          a: answer,
          isRedFlag: resp.is_red_flag
        }
      ]);

      if (resp.is_red_flag) {
        setActiveRedFlag({
          detected: true,
          reason: resp.red_flag_reason || 'Priority clinical symptom detected.'
        });
      }

      setVoiceState('understood');
      setTextAnswer('');
      resetTranscript();

      // Fetch next question
      await fetchNextQuestion(sessionId);
    } catch {
      setHistoryTurns(prev => [
        ...prev,
        { q: currentQuestion.question_text, a: answer, isRedFlag: false }
      ]);
      setTextAnswer('');
      resetTranscript();
      await fetchNextQuestion(sessionId);
    } finally {
      setIsSubmitting(false);
      setVoiceState('idle');
    }
  };

  return (
    <PatientLayout currentStep={3} onResetSession={() => navigate('/')}>
      <div className="max-w-3xl mx-auto w-full space-y-6 animate-fadeIn">
        {/* Red Flag Emergency Banner if triggered */}
        {activeRedFlag?.detected && (
          <RedFlagAlertBanner
            reason={activeRedFlag.reason}
            onAcknowledge={() => setActiveRedFlag(null)}
          />
        )}

        {/* The Central Question Hero Card */}
        <div className="bg-white rounded-3xl border border-surface-border p-8 md:p-12 shadow-xl space-y-8 text-center">
          <div className="flex justify-between items-center text-xs text-text-secondary border-b border-surface-border pb-3">
            <span className="font-mono uppercase font-bold text-clinical-700 tracking-wider">
              {currentQuestion?.question_key ? `Topic: ${currentQuestion.question_key.replace(/_/g, ' ')}` : 'Medical Interview'}
            </span>
            {currentQuestion?.question_text && (
              <AudioAssistantButton
                textToSpeak={currentQuestion.question_text}
                lang={cookieStorage.get('medikiosk_language') || 'en'}
                size="sm"
              />
            )}
          </div>

          {/* Central Dominant Question Prompt */}
          <div className="py-2">
            <h2 className="text-3xl sm:text-4xl md:text-4xl font-extrabold text-navy-950 tracking-tight leading-snug">
              {currentQuestion?.question_text || 'Loading medical question...'}
            </h2>
          </div>

          {/* Voice Waveform & Microphone Action */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 shadow-inner">
            <VoiceWaveform
              state={voiceState}
              onToggleRecord={handleToggleVoice}
              transcript={textAnswer}
            />

            {textAnswer.trim() && (
              <button
                onClick={() => submitAnswer(textAnswer)}
                disabled={isSubmitting}
                className="mt-4 px-6 py-3 bg-clinical-600 hover:bg-clinical-700 text-white font-bold rounded-xl shadow-md transition flex items-center justify-center space-x-2 mx-auto active:scale-95"
              >
                <span>Confirm Spoken Answer</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Touch Alternative Choices (Prompt §14) */}
          {currentQuestion?.options && currentQuestion.options.length > 0 && (
            <div className="space-y-3 pt-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Or Tap an Answer (या विकल्प चुनें)
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {currentQuestion.options.map((option, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => submitAnswer(option)}
                    disabled={isSubmitting}
                    className="p-5 rounded-2xl bg-white hover:bg-clinical-50 border-2 border-slate-200 hover:border-clinical-400 text-navy-900 font-bold text-lg md:text-xl text-left transition-all active:scale-98 shadow-sm flex items-center justify-between group kiosk-touch-btn"
                  >
                    <span>{option}</span>
                    <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-clinical-600 transition" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Manual Free-Text Fallback Input */}
          {currentQuestion?.input_type === 'FREE_TEXT_OR_VOICE' && (
            <div className="flex items-center space-x-3 pt-2">
              <input
                type="text"
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && submitAnswer(textAnswer)}
                placeholder="Type your answer here..."
                className="flex-1 h-14 px-4 bg-slate-50 border-2 border-slate-200 rounded-xl font-medium text-navy-950 focus:border-clinical-600 focus:bg-white focus:outline-none transition text-base"
              />
              <button
                onClick={() => submitAnswer(textAnswer)}
                disabled={!textAnswer.trim() || isSubmitting}
                className="h-14 px-6 bg-clinical-600 hover:bg-clinical-700 text-white font-bold rounded-xl transition flex items-center space-x-2 disabled:opacity-50"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Skip / Next Step Action */}
          <div className="flex justify-between items-center text-xs text-slate-400 pt-4 border-t border-slate-100">
            <span>You can speak or tap an answer.</span>
            <button
              onClick={() => navigate('/scan')}
              className="font-semibold text-clinical-600 hover:underline flex items-center space-x-1"
            >
              <span>Skip to Document Scanner →</span>
            </button>
          </div>
        </div>

        {/* Conversation History Drawer (Subtle, non-distracting) */}
        {historyTurns.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-clinical-600" />
              <span>Answers Recorded So Far ({historyTurns.length})</span>
            </h4>
            <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
              {historyTurns.map((turn, i) => (
                <div key={i} className="p-3 bg-slate-50 rounded-xl text-xs space-y-1">
                  <span className="font-semibold text-slate-700 block">Q: {turn.q}</span>
                  <span className="font-bold text-navy-950 block">A: {turn.a}</span>
                  {turn.isRedFlag && (
                    <span className="text-[10px] bg-red-100 text-red-800 px-2 py-0.5 rounded font-bold">
                      Flagged for Doctor Review
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PatientLayout>
  );
};
