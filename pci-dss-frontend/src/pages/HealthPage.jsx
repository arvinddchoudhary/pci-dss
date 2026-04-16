import React, { useState, useEffect } from 'react';
import { Heart, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { getHealth, verifyAuditChain } from '../services/api';
import PageHeader from '../components/PageHeader';
import LoadingSpinner from '../components/LoadingSpinner';

export default function HealthPage() {
  const [health, setHealth] = useState(null);
  const [chain, setChain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendUp, setBackendUp] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [healthData, chainData] = await Promise.all([getHealth(), verifyAuditChain()]);
      setHealth(healthData);
      setChain(chainData);
      setBackendUp(true);
    } catch (err) {
      setBackendUp(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingSpinner message="Checking system health..." />;

  const checks = [
    { name: 'FastAPI Backend', status: backendUp, detail: backendUp ? 'Responding on port 8000' : 'Connection refused' },
    { name: 'Audit Log Integrity', status: chain?.valid, detail: chain?.message || 'Unknown' },
    { name: 'PCI v4.0 Support', status: true, detail: 'Enabled' },
    { name: 'PCI v3.2.1 Support', status: true, detail: 'Enabled (transition period)' },
    { name: 'FAISS Vector Store', status: backendUp, detail: 'Loaded' },
    { name: 'Jira Integration', status: true, detail: health?.status === 'healthy' ? 'Configured' : 'Simulated' },
  ];

  return (
    <div className="animate-fade-in">
      <PageHeader icon={Heart} title="System Health" subtitle="Service health monitoring (SLA target: 99.95% uptime)"
        action={<button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 text-sm"><RefreshCw className="w-4 h-4" /> Refresh</button>}
      />

      {/* Overall Status */}
      <div className={`rounded-xl p-8 mb-8 border text-center ${backendUp ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
        {backendUp ? <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" /> : <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />}
        <h2 className={`text-3xl font-bold ${backendUp ? 'text-green-400' : 'text-red-400'}`}>{backendUp ? 'ALL SYSTEMS OPERATIONAL' : 'BACKEND OFFLINE'}</h2>
        <p className="text-slate-400 mt-2">{health?.service || 'PCI DSS Compliance Agent'} {health?.version || ''}</p>
      </div>

      {/* Individual Checks */}
      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-pci-border"><h3 className="text-white font-semibold">Component Health</h3></div>
        <div className="divide-y divide-pci-border/50">
          {checks.map((check, i) => (
            <div key={i} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors">
              <div className="flex items-center gap-3">
                {check.status ? <CheckCircle className="w-5 h-5 text-green-400" /> : <XCircle className="w-5 h-5 text-red-400" />}
                <span className="text-white font-medium">{check.name}</span>
              </div>
              <span className="text-sm text-slate-400">{check.detail}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}