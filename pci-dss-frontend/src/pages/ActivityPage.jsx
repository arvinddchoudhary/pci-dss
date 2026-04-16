import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { getAgentActivity } from '../services/api';
import PageHeader from '../components/PageHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function ActivityPage() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await getAgentActivity(100);
      setActivities(data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingSpinner message="Loading agent activity..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  const getActionColor = (action) => {
    if (action?.includes('ERROR')) return 'text-red-400';
    if (action?.includes('COMPLETE')) return 'text-green-400';
    if (action?.includes('START')) return 'text-blue-400';
    if (action?.includes('APPROVAL')) return 'text-amber-400';
    if (action?.includes('TICKET')) return 'text-purple-400';
    return 'text-slate-400';
  };

  return (
    <div className="animate-fade-in">
      <PageHeader icon={Activity} title="Agent Activity Log"
        subtitle="Full audit trail of every action taken by the AI agent (Constraint C3)"
        action={
          <button onClick={fetchData} className="px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 text-sm">
            Refresh
          </button>
        }
      />

      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="divide-y divide-pci-border/50 max-h-[700px] overflow-y-auto">
          {[...activities].reverse().map((act, i) => (
            <div key={i} className="p-4 hover:bg-white/5 transition-colors font-mono text-sm animate-slide-in" style={{ animationDelay: `${i * 15}ms` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 w-24">{act.agent_name}</span>
                  <span className={`text-xs font-semibold ${getActionColor(act.action)}`}>{act.action}</span>
                  {act.system_id && <span className="text-xs text-blue-400">{act.system_id}</span>}
                </div>
                <div className="flex items-center gap-3">
                  {act.duration_ms && <span className="text-xs text-slate-600">{act.duration_ms.toFixed(0)}ms</span>}
                  <span className="text-xs text-slate-600">{act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : ''}</span>
                </div>
              </div>
              {act.details && <p className="text-xs text-slate-500 mt-1 ml-28">{act.details}</p>}
            </div>
          ))}
          {activities.length === 0 && (
            <div className="p-12 text-center text-slate-500">No agent activity recorded yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}