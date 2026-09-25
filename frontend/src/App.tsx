/**
 * MediKiosk React Main Application Component
 * ===========================================
 * 
 * Enforces Prompt Specifications:
 * §7: Global Application Structure
 *     /                     -> Welcome / Landing Page
 *     /identify             -> Patient ABHA identification
 *     /consent              -> Informed consent card
 *     /converse             -> Adaptive Voice/Touch symptom interview (Hero Screen)
 *     /scan                 -> Prescription/Report OCR scanner
 *     /summary              -> AI case summary & Physician Review
 *     /consult              -> Consultation-ready view & Timeline
 *     /doctor               -> High-information Doctor consultation console
 *     /doctor/session/:id   -> Doctor session review
 *     /demo                 -> SIH Judge Deterministic Demo Runner
 * 
 * §41: Strict Privacy & Security
 *     Pure cookie storage mechanism (zero localStorage / sessionStorage).
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Pages
import { WelcomePage } from './pages/WelcomePage';
import { IdentifyPage } from './pages/Identify/IdentifyPage';
import { ConsentPage } from './pages/Consent/ConsentPage';
import { ConversePage } from './pages/Converse/ConversePage';
import { ScanPage } from './pages/Scan/ScanPage';
import { SummaryPage } from './pages/Summary/SummaryPage';
import { ConsultPage } from './pages/Consult/ConsultPage';
import { DoctorDashboardPage } from './pages/Doctor/DoctorDashboardPage';
import { DemoRunnerPage } from './pages/Demo/DemoRunnerPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Welcome / Landing Screen (§8) */}
        <Route path="/" element={<WelcomePage />} />

        {/* Patient Guided Intake Flow (§7, §10, §11, §12, §19, §22, §25) */}
        <Route path="/identify" element={<IdentifyPage />} />
        <Route path="/consent" element={<ConsentPage />} />
        <Route path="/converse" element={<ConversePage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/summary" element={<SummaryPage />} />
        <Route path="/consult" element={<ConsultPage />} />

        {/* High-Information Clinical Doctor Console (§18, §25) */}
        <Route path="/doctor" element={<DoctorDashboardPage />} />
        <Route path="/doctor/session/:id" element={<DoctorDashboardPage />} />

        {/* SIH Judge Deterministic Demonstration Runner (§35) */}
        <Route path="/demo" element={<DemoRunnerPage />} />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
