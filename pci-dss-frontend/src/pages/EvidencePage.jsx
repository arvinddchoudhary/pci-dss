import React, { useState, useEffect } from 'react';
import { Package, CheckCircle, XCircle } from 'lucide-react';
import { getAllEvidence, getEvidenceCompleteness } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function EvidencePage() {
  const [evidence, setEvidence] = useState([]);
  const [completeness, setCompleteness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [evData, compData] = await Promise.all([getAllEvidence(), getEvidenceCompleteness()]);
      setEvidence(evData || []);
      setCompleteness(compData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingSpinner message="Loading evidence packages..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div className="animate-fade-in">
      <PageHeader icon={Package} title="Evidence Packages" subtitle="Automated evidence collection mapped to PCI DSS controls" />

      {/* Completeness Report */}
      {completeness && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard icon={Package} label="Total Artifacts" value={evidence.length} color="blue" />
          <StatCard icon={CheckCircle} label="Covered Reqs" value={`${completeness.covered}/${completeness.total_required}`} color="green" />
          <StatCard
            icon={completeness.meets_kpi ? CheckCircle : XCircle}
            label="Completeness" value={`${completeness.completeness_pct}%`}
            subtext={completeness.meets_kpi ? '✅ Meets 85% KPI' : '❌ Below 85% KPI'}
            color={completeness.meets_kpi ? 'green' : 'red'}
          />
          <StatCard icon={XCircle} label="Missing" value={completeness.missing?.length || 0}
            subtext={completeness.missing?.slice(0, 2).join(', ') || 'None'} color="amber" />
        </div>
      )}

      {/* Evidence List */}
      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="p-6 border-b border-pci-border">
          <h3 className="text-white font-semibold">Collected Evidence ({evidence.length} artifacts)</h3>
        </div>
        <div className="divide-y divide-pci-border/50 max-h-[600px] overflow-y-auto">
          {evidence.map((ev, i) => (
            <div key={i} className="p-4 hover:bg-white/5 transition-colors animate-slide-in" style={{ animationDelay: `${i * 20}ms` }}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs">{ev.evidence_type}</span>
                  <span className="font-mono text-sm text-purple-400">{ev.pci_requirement}</span>
                </div>
                <span className="text-xs text-slate-500">{ev.collected_at ? new Date(ev.collected_at).toLocaleString() : ''}</span>
              </div>
              <p className="text-sm text-slate-300">{ev.system_id}</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-slate-500">Hash:</span>
                <span className="font-mono text-xs text-green-400">{ev.hash?.substring(0, 24)}...</span>
              </div>
            </div>
          ))}
          {evidence.length === 0 && (
            <div className="p-12 text-center text-slate-500">No evidence collected yet. Run scans to generate evidence.</div>
          )}
        </div>
      </div>
    </div>
  );
}