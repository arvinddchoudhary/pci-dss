import React, { useState, useEffect } from 'react';
import { ScrollText, ShieldCheck, ShieldAlert, RefreshCw } from 'lucide-react';
import { getAuditLog, verifyAuditChain } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [chainStatus, setChainStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [verifying, setVerifying] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [logData, chainData] = await Promise.all([getAuditLog(50), verifyAuditChain()]);
      setLogs(logData || []);
      setChainStatus(chainData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const data = await verifyAuditChain();
      setChainStatus(data);
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingSpinner message="Loading audit trail..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div className="animate-fade-in">
      <PageHeader icon={ScrollText} title="Immutable Audit Log"
        subtitle="Constraint C3: All agent actions logged immutably with hash chain integrity"
        action={
          <button onClick={handleVerify} disabled={verifying}
            className="flex items-center gap-2 px-4 py-2 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-lg hover:bg-purple-500/20 text-sm">
            {verifying ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            Verify Chain
          </button>
        }
      />

      {/* Chain Integrity Status */}
      {chainStatus && (
        <div className={`rounded-xl p-5 mb-6 border ${chainStatus.valid ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
          <div className="flex items-center gap-3">
            {chainStatus.valid ? <ShieldCheck className="w-6 h-6 text-green-400" /> : <ShieldAlert className="w-6 h-6 text-red-400" />}
            <div>
              <p className={`font-semibold ${chainStatus.valid ? 'text-green-400' : 'text-red-400'}`}>{chainStatus.message}</p>
              <p className="text-sm text-slate-400">{chainStatus.entries} entries verified</p>
            </div>
          </div>
          {chainStatus.broken_links?.length > 0 && (
            <div className="mt-3 space-y-1">
              {chainStatus.broken_links.map((link, i) => (
                <p key={i} className="text-xs text-red-400 font-mono">⚠️ Entry #{link.entry_index}: {link.issue}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Log Entries */}
      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-pci-border">
          <h3 className="text-white font-semibold">Recent Entries ({logs.length})</h3>
        </div>
        <div className="divide-y divide-pci-border/50 max-h-[600px] overflow-y-auto">
          {[...logs].reverse().map((log, i) => (
            <div key={i} className="p-4 hover:bg-white/5 transition-colors text-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <StatusBadge status={log.status} />
                  <span className="text-white font-medium">{log.system_id}</span>
                  {log.violated_rule && <span className="font-mono text-xs text-blue-400">{log.violated_rule}</span>}
                </div>
                <div className="flex items-center gap-3">
                  {log.risk_score && (
                    <span className={`text-sm font-bold ${log.risk_score >= 8 ? 'text-red-400' : log.risk_score >= 5 ? 'text-amber-400' : 'text-green-400'}`}>
                      Risk: {log.risk_score}
                    </span>
                  )}
                  {log.ticket_id && <span className="font-mono text-xs text-slate-500">{log.ticket_id}</span>}
                </div>
              </div>
              {log.reasoning && <p className="text-slate-400 text-xs mt-1 truncate">{log.reasoning}</p>}
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-600">
                <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : ''}</span>
                {log.hash && <span className="font-mono">Hash: {log.hash.substring(0, 16)}...</span>}
                {log.previous_hash && <span className="font-mono">Prev: {log.previous_hash.substring(0, 12)}...</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}