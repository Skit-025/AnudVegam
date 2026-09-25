/**
 * Clinical Source & Provenance Badge
 * ===================================
 * 
 * Enforces strict clinical clarity (Prompt §23):
 * Distinguishes patient-reported vs OCR document extracted vs AI-drafted vs Physician-verified data.
 */

import React from 'react';
import { User, FileText, Sparkles, CheckCircle2 } from 'lucide-react';

export type ProvenanceSource = 'patient' | 'document' | 'ai' | 'physician';

interface SourceBadgeProps {
  source: ProvenanceSource;
  confidence?: number;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source, confidence }) => {
  const configs = {
    patient: {
      label: 'Patient reported',
      icon: User,
      bg: 'bg-sky-50',
      text: 'text-sky-800',
      border: 'border-sky-200'
    },
    document: {
      label: 'Document extracted',
      icon: FileText,
      bg: 'bg-purple-50',
      text: 'text-purple-800',
      border: 'border-purple-200'
    },
    ai: {
      label: 'AI drafted',
      icon: Sparkles,
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200'
    },
    physician: {
      label: 'Physician verified',
      icon: CheckCircle2,
      bg: 'bg-emerald-50',
      text: 'text-emerald-800',
      border: 'border-emerald-200'
    }
  }[source];

  const Icon = configs.icon;

  return (
    <span
      className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${configs.bg} ${configs.text} ${configs.border}`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{configs.label}</span>
      {confidence !== undefined && (
        <span className="opacity-75 font-mono ml-1">({Math.round(confidence * 100)}%)</span>
      )}
    </span>
  );
};
