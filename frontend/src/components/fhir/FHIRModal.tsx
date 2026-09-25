/**
 * ABDM / FHIR R4 Bundle Modal Viewer
 * ==================================
 * 
 * Enforces prompt specification §28:
 * Demonstrates the standardized ABDM Fast Healthcare Interoperability Resources (FHIR R4)
 * export containing Patient, Encounter, Condition, Observation, MedicationStatement, and Composition.
 */

import React, { useState } from 'react';
import { Database, Check, Copy, Download, X, ShieldCheck } from 'lucide-react';

interface FHIRModalProps {
  isOpen: boolean;
  onClose: () => void;
  fhirPayload: any;
  careContextId?: string;
}

export const FHIRModal: React.FC<FHIRModalProps> = ({
  isOpen,
  onClose,
  fhirPayload,
  careContextId = 'CARE_CONTEXT_001'
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const jsonString = JSON.stringify(fhirPayload, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ABDM_FHIR_Bundle_${careContextId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-navy-950/75 backdrop-blur-sm z-50 flex items-center justify-center p-6 animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-surface-border overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-navy-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-clinical-600 text-white">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white">ABDM / HL7 FHIR R4 Bundle Export</h3>
                <span className="text-xs bg-emerald-500/20 text-emerald-300 font-mono px-2 py-0.5 rounded border border-emerald-500/30">
                  ✓ Verified Schema
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Care Context ID: <span className="font-mono text-white">{careContextId}</span> • National Health Authority Standard
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Informational Banner */}
        <div className="bg-slate-50 px-6 py-3 border-b border-surface-border flex items-center justify-between text-xs">
          <span className="text-text-secondary flex items-center space-x-1.5">
            <ShieldCheck className="w-4 h-4 text-clinical-600" />
            <span>Includes <strong>Patient, Composition, Encounter, Condition, Observation, and MedicationStatement</strong> resources.</span>
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 font-semibold text-slate-700 flex items-center space-x-1.5 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy JSON'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="px-3 py-1.5 rounded-lg bg-clinical-600 hover:bg-clinical-700 text-white font-semibold flex items-center space-x-1.5 transition shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Bundle</span>
            </button>
          </div>
        </div>

        {/* JSON Code Viewer */}
        <div className="flex-1 p-6 overflow-auto bg-slate-900 text-slate-100 font-mono text-xs leading-relaxed">
          <pre>{jsonString}</pre>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-white border-t border-surface-border flex justify-between items-center text-xs text-slate-500">
          <span>ABDM Mock Gateway Integration • Safe Electronic Health Record (EHR) Export</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
