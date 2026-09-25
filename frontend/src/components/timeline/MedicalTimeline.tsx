/**
 * Medical Timeline Component — Major WOW Feature
 * ===============================================
 * 
 * Enforces prompt specification §21:
 * Interactive chronological clinical timeline tracking past medical events,
 * medication introductions, lab report trends, and active complaints.
 * Features expandable event cards with source verification, confidence, and document references.
 */

import React, { useState } from 'react';
import { Calendar, Activity, Pill, FileText, ChevronDown, ChevronUp, AlertCircle, Sparkles } from 'lucide-react';
import { SourceBadge, ProvenanceSource } from '../kiosk/SourceBadge';

export interface TimelineEventItem {
  id: string;
  year: string;
  date: string;
  title: string;
  category: 'DIAGNOSIS' | 'MEDICATION' | 'LAB' | 'COMPLAINT';
  value?: string;
  source: ProvenanceSource;
  sourceDocument?: string;
  confidence?: number;
  isAbnormal?: boolean;
  notes?: string;
}

export const DEFAULT_TIMELINE_EVENTS: TimelineEventItem[] = [
  {
    id: 'tl-1',
    year: '2019',
    date: '14 Oct 2019',
    title: 'Type 2 Diabetes Mellitus Diagnosed',
    category: 'DIAGNOSIS',
    value: 'Fasting Sugar: 178 mg/dL',
    source: 'document',
    sourceDocument: 'Civil Hospital OPD Slip #10492',
    confidence: 0.96,
    notes: 'Initial diagnosis by internal medicine OPD. Lifestyle modification advised.'
  },
  {
    id: 'tl-2',
    year: '2021',
    date: '02 Mar 2021',
    title: 'Metformin & Amlodipine Started',
    category: 'MEDICATION',
    value: 'Tab Metformin 500mg BD + Tab Amlodipine 5mg OD',
    source: 'document',
    sourceDocument: 'Prescription Slip — Dr. R. Verma',
    confidence: 0.94,
    notes: 'Initiated for glycemic control and mild essential hypertension.'
  },
  {
    id: 'tl-3',
    year: '2024',
    date: '18 Nov 2024',
    title: 'Glycated Hemoglobin (HbA1c) Test',
    category: 'LAB',
    value: 'HbA1c: 8.2% (Reference: 4.0 - 5.6%)',
    source: 'document',
    sourceDocument: 'Pathology Blood Report — SRL Diagnostics',
    confidence: 0.98,
    isAbnormal: true,
    notes: 'Uncontrolled blood glycemic index. Dose adjustment recommended.'
  },
  {
    id: 'tl-4',
    year: '2026',
    date: 'Recent',
    title: 'Previous Prescription Re-fill',
    category: 'MEDICATION',
    value: 'Tab Pantoprazole 40mg added for reflux',
    source: 'document',
    sourceDocument: 'Scanned Prescription Document',
    confidence: 0.92
  },
  {
    id: 'tl-5',
    year: '2026',
    date: 'Today',
    title: 'Current OPD Visit: Acute Symptom Intake',
    category: 'COMPLAINT',
    value: 'Chief Complaint: Retrosternal Chest Discomfort',
    source: 'patient',
    confidence: 1.0,
    isAbnormal: true,
    notes: 'Reported during MediKiosk intake interview. Prioritized for ECG.'
  }
];

interface MedicalTimelineProps {
  events?: TimelineEventItem[];
  compact?: boolean;
}

export const MedicalTimeline: React.FC<MedicalTimelineProps> = ({
  events = DEFAULT_TIMELINE_EVENTS,
  compact = false
}) => {
  const [expandedId, setExpandedId] = useState<string | null>('tl-5');

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'DIAGNOSIS':
        return <Activity className="w-4 h-4 text-blue-600" />;
      case 'MEDICATION':
        return <Pill className="w-4 h-4 text-emerald-600" />;
      case 'LAB':
        return <FileText className="w-4 h-4 text-purple-600" />;
      case 'COMPLAINT':
      default:
        return <AlertCircle className="w-4 h-4 text-amber-600" />;
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-surface-border p-6 shadow-sm">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-surface-border">
        <div>
          <h3 className="text-xl font-bold text-navy-900 flex items-center space-x-2">
            <span>Patient Chronological Medical Timeline</span>
            <Sparkles className="w-5 h-5 text-clinical-600" />
          </h3>
          <p className="text-xs text-text-secondary mt-0.5">
            Synthesized from historical records, uploaded documents, and current kiosk interview
          </p>
        </div>
        <span className="text-xs bg-slate-100 text-slate-700 font-semibold px-3 py-1 rounded-full border">
          {events.length} Milestones
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:content-[''] before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
        {events.map((evt) => {
          const isExpanded = expandedId === evt.id;
          return (
            <div key={evt.id} className="relative group">
              {/* Timeline marker node */}
              <div
                className={`absolute -left-6 top-1.5 w-6 h-6 rounded-full border-2 bg-white flex items-center justify-center shadow-sm transition-all ${
                  evt.isAbnormal
                    ? 'border-red-500 text-red-600 ring-2 ring-red-100'
                    : 'border-clinical-600 text-clinical-600'
                }`}
              >
                {getCategoryIcon(evt.category)}
              </div>

              {/* Event Card */}
              <div
                onClick={() => toggleExpand(evt.id)}
                className={`ml-3 p-4 rounded-xl border transition-all cursor-pointer ${
                  isExpanded
                    ? 'bg-slate-50 border-clinical-300 shadow-sm'
                    : 'bg-white border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs font-bold font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {evt.year}
                    </span>
                    <h4 className="text-base font-bold text-navy-900">{evt.title}</h4>
                    {evt.isAbnormal && (
                      <span className="text-xs font-bold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full">
                        Flagged
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3">
                    <SourceBadge source={evt.source} confidence={evt.confidence} />
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                </div>

                {evt.value && (
                  <p className="text-sm text-clinical-900 font-medium mt-1 ml-11">
                    {evt.value}
                  </p>
                )}

                {/* Expanded Details Panel */}
                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-slate-200 text-xs space-y-2 ml-11 animate-fadeIn">
                    <div className="grid grid-cols-2 gap-2 text-text-secondary">
                      <div>
                        <span className="font-semibold text-slate-700">Recorded Date: </span>
                        <span>{evt.date}</span>
                      </div>
                      <div>
                        <span className="font-semibold text-slate-700">Source Document: </span>
                        <span>{evt.sourceDocument || 'Direct Patient Input'}</span>
                      </div>
                    </div>

                    {evt.notes && (
                      <p className="bg-white p-2.5 rounded-lg border border-slate-200 text-slate-700">
                        {evt.notes}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
