import React, { useState, useEffect } from 'react';
import { Shield, Clock, AlertTriangle, User } from 'lucide-react';
import { getRemediation } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function RemediationPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const result = await getRemediation();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <LoadingSpinner message="Loading remediation workplan..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div className="animate-fade-in">
      <PageHeader icon={Shield} title="Remediation Workplan" subtitle="Prioritized remediation tasks with owner assignment, SLA tracking, and escalation" />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Shield} label="Total Tasks" value={data?.total_tasks || 0} color="blue" />
        <StatCard icon={AlertTriangle} label="Critical" value={data?.critical_count || 0} subtext="24h SLA" color="red" />
        <StatCard icon={Clock} label="High" value={data?.high_count || 0} subtext="48h SLA" color="amber" />
        <StatCard icon={AlertTriangle} label="Escalated" value={data?.escalated_count || 0} subtext="Past SLA deadline" color="purple" />
      </div>

      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-pci-border">
                <th className="text-left p-4 text-xs text-slate-400 uppercase">Task ID</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">System</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">Rule</th>
                <th className="text-center p-4 text-xs text-slate-400 uppercase">Severity</th>
                <th className="text-center p-4 text-xs text-slate-400 uppercase">Status</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">Owner</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">SLA</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">Deadline</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase">Ticket</th>
              </tr>
            </thead>
            <tbody>
              {data?.tasks?.map((task, i) => (
                <tr key={i} className="border-b border-pci-border/50 hover:bg-white/5 transition-colors animate-slide-in" style={{ animationDelay: `${i * 30}ms` }}>
                  <td className="p-4 font-mono text-xs text-blue-400">{task.task_id}</td>
                  <td className="p-4 text-sm text-white">{task.system_id}</td>
                  <td className="p-4 font-mono text-xs text-slate-300">{task.violated_rule || '—'}</td>
                  <td className="p-4 text-center"><StatusBadge status={task.severity} /></td>
                  <td className="p-4 text-center"><StatusBadge status={task.status} /></td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <User className="w-3 h-3 text-slate-500" />
                      <span className="text-sm text-purple-400">{task.owner}</span>
                    </div>
                    <span className="text-xs text-slate-500">{task.assigned_to}</span>
                  </td>
                  <td className="p-4 text-sm text-slate-400">{task.sla_hours}h</td>
                  <td className="p-4 text-xs text-slate-400">{task.deadline ? new Date(task.deadline).toLocaleString() : '—'}</td>
                  <td className="p-4 font-mono text-xs text-blue-400">{task.ticket_id || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {(!data?.tasks || data.tasks.length === 0) && (
          <div className="p-12 text-center text-slate-500">No remediation tasks found. Run scans first to generate violations.</div>
        )}
      </div>
    </div>
  );
}