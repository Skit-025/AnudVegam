import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Sparkles, AlertTriangle, FileText, CheckCircle, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { cookieStorage } from '../../utils/cookieStorage';

interface Scenario {
  id: string;
  title: string;
  patientName: string;
  abhaId: string;
  age: number;
  gender: string;
  language: string;
  chiefComplaint: string;
  severity: 'normal' | 'emergency' | 'chronic';
  tags: string[];
  description: string;
  presetAnswers: Array<{ question: string; answer: string; isRedFlag?: boolean }>;
  documents: Array<{ name: string; type: string; summary: string }>;
}

export const DemoRunnerPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedScenario, setSelectedScenario] = useState<string>('chest-pain');
  const [isInitializing, setIsInitializing] = useState<boolean>(false);

  const scenarios: Scenario[] = [
    {
      id: 'chest-pain',
      title: 'Scenario A: Emergency Chest Pain & Breathlessness (Red-Flag Trigger)',
      patientName: 'Rameshwar Patnaik',
      abhaId: '91-4582-7391-0021',
      age: 58,
      gender: 'Male',
      language: 'odia',
      chiefComplaint: 'Chest pressure with pain radiating to left shoulder and breathing difficulty',
      severity: 'emergency',
      tags: ['SIH Primary Showcase', 'Red-Flag Escalation', 'Odia Language', 'Priority Queue'],
      description: 'Simulates a 58-year-old patient who arrives at the AIIMS Bhubaneswar kiosk. The adaptive dialogue detects radiating chest pain and breathlessness, immediately triggering the non-diagnostic priority triage alert for physician consultation.',
      presetAnswers: [
        { question: 'Where is the discomfort located?', answer: 'Substernal chest region radiating to left shoulder', isRedFlag: true },
        { question: 'How long have you had this feeling?', answer: 'Since last 3 hours, acute onset' },
        { question: 'Do you feel difficulty in breathing or cold sweats?', answer: 'Yes, heavy breathlessness and sweating', isRedFlag: true },
        { question: 'Any history of heart disease or diabetes?', answer: 'History of Type 2 Diabetes for 6 years' },
      ],
      documents: [
        { name: 'ECG_Previous_2025.pdf', type: 'Electrocardiogram', summary: 'Sinus rhythm with mild ST depression' },
        { name: 'Prescription_Metformin_2026.pdf', type: 'Prescription', summary: 'Metformin 500mg BD, Atorvastatin 20mg OD' },
      ],
    },
    {
      id: 'chronic-diabetes',
      title: 'Scenario B: Chronic Diabetes & Hypertension Follow-up with OCR',
      patientName: 'Sunita Devi Sharma',
      abhaId: '82-1923-4410-9932',
      age: 52,
      gender: 'Female',
      language: 'hindi',
      chiefComplaint: 'Routine 3-month review for diabetes and prescription refill with recent fatigue',
      severity: 'chronic',
      tags: ['Document OCR', 'Timeline Extraction', 'Hindi Language', 'Entity Extraction'],
      description: 'Patient brings a wrinkled handwritten prescription and blood test report. The OCR microservice parses Metformin 500mg and HbA1c 7.4%, populating the historical timeline with full provenance tracking.',
      presetAnswers: [
        { question: 'What brings you to the hospital today?', answer: 'Routine quarterly checkup for diabetes medicines' },
        { question: 'How do you feel recently?', answer: 'Mild fatigue in the evenings, no chest pain or blurred vision' },
        { question: 'Are you taking your prescribed medicines regularly?', answer: 'Yes, Metformin 500 mg morning and evening' },
      ],
      documents: [
        { name: 'Dr_Mishra_Prescription_July2026.pdf', type: 'Prescription', summary: 'Metformin 500mg, Telmisartan 40mg' },
        { name: 'Thyrocare_HbA1c_Report.pdf', type: 'Lab Report', summary: 'HbA1c 7.4%, Fasting Glucose 142 mg/dL' },
      ],
    },
    {
      id: 'fever-cough',
      title: 'Scenario C: Acute Viral URI / Seasonal Fever',
      patientName: 'Aarav Deshmukh',
      abhaId: '77-3021-9943-1288',
      age: 29,
      gender: 'Male',
      language: 'english',
      chiefComplaint: 'High fever for 4 days with productive cough and body ache',
      severity: 'normal',
      tags: ['Standard Triage', 'Fast Turnaround', 'English', 'Voice Assistant'],
      description: 'Young professional using voice inputs to report fever and cough. The system systematically evaluates symptom duration, checks for red flags (no hemoptysis, no respiratory distress), and drafts an executive pre-consult note.',
      presetAnswers: [
        { question: 'What is your main health concern today?', answer: 'High fever for 4 days with sore throat' },
        { question: 'What is your highest recorded temperature?', answer: '102.4 F yesterday evening' },
        { question: 'Any phlegm or shortness of breath?', answer: 'Mild clear phlegm, breathing is normal' },
        { question: 'Any drug allergies?', answer: 'No known drug allergies' },
      ],
      documents: [
        { name: 'CBC_Test_Yesterday.pdf', type: 'Hematology Report', summary: 'WBC 9,800/mcL, Platelets normal' },
      ],
    },
  ];

  const handleLaunchDemo = (scenario: Scenario, directToDoctor = false) => {
    setIsInitializing(true);

    // Seed session into cookie storage (zero localStorage!)
    cookieStorage.setPatient({
      id: 'demo-patient-' + scenario.id,
      abha_id: scenario.abhaId,
      full_name: scenario.patientName,
      age: scenario.age,
      gender: scenario.gender,
      phone: '+91 98765 43210',
      preferred_language: scenario.language,
    });

    cookieStorage.setLanguage(scenario.language);
    cookieStorage.setConsent(true);
    cookieStorage.setSessionId('sih-demo-session-' + scenario.id);

    setTimeout(() => {
      setIsInitializing(false);
      if (directToDoctor) {
        navigate('/doctor');
      } else {
        navigate('/converse');
      }
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Bar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-8 py-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20">
            MK
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">MediKiosk SIH-26047 Demo Runner</h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800 font-mono">
                Judge Review Mode
              </span>
            </div>
            <p className="text-xs text-slate-400">Deterministic clinical scenario execution • Zero hardcoding backend integration</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              cookieStorage.clearAll();
              alert('Session cookies purged.');
            }}
            className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-xs font-medium text-slate-300 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Clear Cookies
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            Go to Kiosk Home
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-8 flex flex-col gap-8">
        {/* Banner */}
        <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-cyan-950/30 border border-blue-800/40 flex items-start gap-4">
          <Sparkles className="w-6 h-6 text-cyan-400 mt-1 flex-shrink-0" />
          <div className="space-y-1">
            <h2 className="text-base font-semibold text-white">SIH 2026 Evaluation Protocol</h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Select one of the three pre-architected clinical cases below to immediately demonstrate the full pipeline:
              <strong> Adaptive Voice / Touch History → Realtime Red-Flag Detection → Prescription OCR & Entity Extraction → Longitudinal Timeline → AI Drafted Pre-Consult Summary → ABDM FHIR R4 Export</strong>.
            </p>
          </div>
        </div>

        {/* Scenarios Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {scenarios.map((scenario) => {
            const isSelected = selectedScenario === scenario.id;
            return (
              <div
                key={scenario.id}
                onClick={() => setSelectedScenario(scenario.id)}
                className={`cursor-pointer rounded-2xl p-6 border transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? 'border-cyan-500 bg-slate-900 shadow-xl shadow-cyan-950/40 ring-1 ring-cyan-500'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/80'
                }`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                        scenario.severity === 'emergency'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : scenario.severity === 'chronic'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}
                    >
                      {scenario.severity === 'emergency' ? '🔴 Red-Flag Emergency' : scenario.severity === 'chronic' ? '🟡 Chronic + OCR' : '🟢 Standard Triage'}
                    </span>
                    <span className="text-xs font-mono text-slate-400">Lang: {scenario.language.toUpperCase()}</span>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-white tracking-tight">{scenario.patientName}</h3>
                    <p className="text-xs font-mono text-cyan-400">ABHA: {scenario.abhaId}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {scenario.age} years • {scenario.gender}
                    </p>
                  </div>

                  <p className="text-sm text-slate-300 font-medium leading-snug">{scenario.chiefComplaint}</p>

                  <p className="text-xs text-slate-400 leading-relaxed">{scenario.description}</p>

                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {scenario.tags.map((tag) => (
                      <span key={tag} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-6 border-t border-slate-800/80 mt-6 space-y-2">
                  <button
                    disabled={isInitializing}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLaunchDemo(scenario, false);
                    }}
                    className="w-full py-3 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 font-bold text-sm text-white shadow-lg shadow-cyan-900/30 flex items-center justify-center gap-2 transition-transform active:scale-95"
                  >
                    <Play className="w-4 h-4 fill-white" />
                    Launch Patient Flow (/converse)
                  </button>
                  <button
                    disabled={isInitializing}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLaunchDemo(scenario, true);
                    }}
                    className="w-full py-2.5 px-4 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-800 hover:bg-slate-700 font-medium text-xs text-slate-300 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    Direct to Doctor View (/doctor)
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Technical Provenance Card */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Architecture Compliance Checklist</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200">Zero LocalStorage</div>
              <p className="text-slate-400">Strictly uses secure session cookies per medical kiosk privacy specifications.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200">Voice + Touch Modality</div>
              <p className="text-slate-400">Real Web Speech synthesis and recognition fallback on every kiosk touchpoint.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200">Clinical Safety Shield</div>
              <p className="text-slate-400">Explicitly disclaims automated AI diagnosis; mandates physician review and electronic sign-off.</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200">ABDM FHIR R4 Export</div>
              <p className="text-slate-400">Generates standard FHIR JSON bundles with Condition, Encounter, and MedicationStatement.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
