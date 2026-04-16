import React, { useState, useEffect } from 'react';
import { UserCheck, Check, X } from 'lucide-react';
import { getApprovals, reviewApproval } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviewer, setReviewer] = useState('');
  const [processing, setProcessing] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await getApprovals();
      setApprovals(data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleReview = async (violationId, action) => {
    if (!reviewer.trim()) {
      alert('Please enter your name as reviewer');
      return;
    }
    setProcessing(violationId);
    try {
      await reviewApproval(violationId, action, reviewer);
      await fetchData();
    } catch (err) {
      alert('Review failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setProcessing(null);
    }
  };

  if (loading) return <LoadingSpinner message="Loading approval queue..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  const pending = approvals.filter(a => a.status === 'PENDING');
  const resolved = approvals.filter(a => a.status !== 'PENDING');

  return (
    <div className="animate-fade-in">
      <PageHeader icon={UserCheck} title="Human-in-the-Loop Approvals"
        subtitle="Constraint C2: No auto-remediation without explicit human approval" />

      {/* Reviewer Input */}
      <div className="bg-pci-card border border-pci-border rounded-xl p-4 mb-6 flex items-center gap-4">
        <label className="text-sm text-slate-400 whitespace-nowrap">Your Name:</label>
        <input
          type="text" value={reviewer} onChange={(e) => setReviewer(e.target.value)}
          placeholder="Enter reviewer name"
          className="bg-pci-dark border border-pci-border rounded-lg px-4 py-2 text-white text-sm focus:border-blue-500 focus:outline-none flex-1 max-w-xs"
        />
      </div>

      {/* Pending Approvals */}
      <div className="mb-8">
        <h3 className="text-white font-semibold mb-4">⏳ Pending Approvals ({pending.length})</h3>
        {pending.length === 0 ? (
          <div className="bg-pci-card border border-pci-border rounded-xl p-8 text-center text-slate-500">
            No pending approvals. All clear! ✅
          </div>
        ) : (
          <div className="space-y-3">
            {pending.map((item, i) => (
              <div key={i} className="bg-pci-card border border-amber-500/20 rounded-xl p-5 animate-pulse-glow">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm text-amber-400">{item.violation_id}</span>
                    <StatusBadge status="PENDING" />
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleReview(item.violation_id, 'APPROVED')}
                      disabled={processing === item.violation_id}
                      className="flex items-center gap-1 px-4 py-2 bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg hover:bg-green-500/20 text-sm">
                      <Check className="w-4 h-4" /> Approve
                    </button>
                    <button onClick={() => handleReview(item.violation_id, 'REJECTED')}
                      disabled={processing === item.violation_id}
                      className="flex items-center gap-1 px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-500/20 text-sm">
                      <X className="w-4 h-4" /> Reject
                    </button>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div><span className="text-xs text-slate-400">System</span><p className="text-white">{item.system_id}</p></div>
                  <div><span className="text-xs text-slate-400">Rule</span><p className="font-mono text-blue-400">{item.violated_rule}</p></div>
                  <div><span className="text-xs text-slate-400">Risk Score</span><p className="text-red-400 font-bold text-lg">{item.risk_score}</p></div>
                  <div><span className="text-xs text-slate-400">Assigned To</span><p className="text-purple-400">{item.assigned_to}</p></div>
                </div>
                <p className="text-sm text-slate-400 mt-2">{item.reasoning}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resolved History */}
      {resolved.length > 0 && (
        <div>
          <h3 className="text-white font-semibold mb-4">📋 Review History ({resolved.length})</h3>
          <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
            <div className="divide-y divide-pci-border/50">
              {resolved.map((item, i) => (
                <div key={i} className="p-4 flex items-center justify-between hover:bg-white/5">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-slate-500">{item.violation_id}</span>
                    <span className="text-sm text-white">{item.system_id}</span>
                    <span className="text-xs text-slate-400">{item.violated_rule}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500">by {item.reviewed_by}</span>
                    <StatusBadge status={item.status} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}