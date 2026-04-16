import React, { useState, useEffect } from 'react';
import { FileText, Download } from 'lucide-react';
import { getQSAReport } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function ReportPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const data = await getQSAReport();
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReport(); }, []);

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `QSA_Report_${report?.report_id || 'export'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <LoadingSpinner message="Generating QSA audit report..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchReport} />;

  return (
    <div className="animate-fade-in">
      <PageHeader
        icon={FileText}
        title="QSA Audit Report"
        subtitle="Audit-ready report with findings, evidence, and compensating controls"
        action={
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg hover:bg-green-500/20 text-sm">
            <Download className="w-4 h-4" /> Export JSON
          </button>
        }
      />

      {/* Report Header */}
      <div className="bg-pci-card border border-pci-border rounded-xl p-6 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div><span className="text-xs text-slate-400">Report ID</span><p className="text-blue-400 font-mono mt-1">{report?.report_id}</p></div>
          <div><span className="text-xs text-slate-400">PCI Version</span><p className="text-white mt-1">{report?.pci_version}</p></div>
          <div><span className="text-xs text-slate-400">Assessment Date</span><p className="text-white mt-1">{report?.assessment_date}</p></div>
          <div><span className="text-xs text-slate-400">Overall Status</span><div className="mt-1"><StatusBadge status={report?.overall_status} size="lg" /></div></div>
        </div>
        <div className="mt-4 pt-4 border-t border-pci-border">
          <span className="text-xs text-slate-400">Summary</span>
          <p className="text-slate-300 text-sm mt-1">{report?.summary}</p>
        </div>
        <div className="mt-4">
          <span className="text-xs text-slate-400">CDE Scope ({report?.cde_scope?.length || 0} systems)</span>
          <div className="flex flex-wrap gap-2 mt-1">
            {report?.cde_scope?.map((sys, i) => (
              <span key={i} className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs font-mono">{sys}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-4">
        {report?.sections?.map((section, i) => (
          <div key={i} className="bg-pci-card border border-pci-border rounded-xl overflow-hidden animate-slide-in" style={{ animationDelay: `${i * 50}ms` }}>
            <div className="p-4 flex items-center justify-between border-b border-pci-border/50">
              <div>
                <span className="font-mono text-blue-400 text-sm">{section.requirement_id}</span>
                <p className="text-white text-sm mt-0.5">{section.requirement_name}</p>
              </div>
              <StatusBadge status={section.status} />
            </div>
            <div className="p-4">
              {section.findings?.map((finding, j) => (
                <p key={j} className="text-slate-400 text-sm mb-1">• {finding}</p>
              ))}
              {section.evidence_refs?.length > 0 && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs text-slate-500">Evidence:</span>
                  {section.evidence_refs.map((ref, j) => (
                    <span key={j} className="text-xs font-mono bg-green-500/10 text-green-400 px-2 py-0.5 rounded">{ref}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}