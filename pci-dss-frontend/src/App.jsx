import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import RemediationPage from './pages/RemediationPage';
import ReportPage from './pages/ReportPage';
import EvidencePage from './pages/EvidencePage';
import ApprovalsPage from './pages/ApprovalPage';
import AuditLogPage from './pages/AuditLogPage';
import ActivityPage from './pages/ActivityPage';
import HealthPage from './pages/HealthPage';

function App() {
  return (
    
      <div className="flex min-h-screen bg-pci-dark">
        <Sidebar />
        <main className="flex-1 p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/remediation" element={<RemediationPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/evidence" element={<EvidencePage />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/audit-log" element={<AuditLogPage />} />
            <Route path="/activity" element={<ActivityPage />} />
            <Route path="/health" element={<HealthPage />} />
          </Routes>
        </main>
      </div>
    
  );
}

export default App;