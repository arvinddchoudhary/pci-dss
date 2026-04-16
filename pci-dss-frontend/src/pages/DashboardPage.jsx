import React, { useState, useEffect } from 'react';
import { LayoutDashboard, AlertTriangle, CheckCircle, XCircle, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { getDashboard } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboard();
      setDashboard(data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDashboard(); }, []);

  if (loading) return <LoadingSpinner message="Loading compliance dashboard..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchDashboard} />;
  if (!dashboard) return null;

  const ragCounts = {
    RED: dashboard.requirements?.filter(r => r.status === 'RED').length || 0,
    AMBER: dashboard.requirements?.filter(r => r.status === 'AMBER').length || 0,
    GREEN: dashboard.requirements?.filter(r => r.status === 'GREEN').length || 0,
  };

  const chartData = dashboard.requirements?.map(r => ({
    name: r.requirement_id.replace('Req ', 'R'),
    violations: r.violations_count,
    status: r.status,
  })) || [];

  const pieData = [
    { name: 'RED', value: ragCounts.RED, color: '#ef4444' },
    { name: 'AMBER', value: ragCounts.AMBER, color: '#f59e0b' },
    { name: 'GREEN', value: ragCounts.GREEN, color: '#22c55e' },
  ].filter(d => d.value > 0);

  const barColors = { RED: '#ef4444', AMBER: '#f59e0b', GREEN: '#22c55e' };

  return (
    <div className="animate-fade-in">
      <PageHeader
        icon={LayoutDashboard}
        title="Compliance Dashboard"
        subtitle="Real-time RAG (Red/Amber/Green) status across all PCI DSS v4.0 requirements"
        action={
          <button onClick={fetchDashboard} className="px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 text-sm">
            Refresh
          </button>
        }
      />

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <StatCard icon={BarChart3} label="Risk Score" value={dashboard.overall_risk_score || 0} subtext="Overall risk (0-10)" color="blue" />
        <StatCard icon={XCircle} label="Violations" value={dashboard.total_violations || 0} subtext="Total findings" color="red" />
        <StatCard icon={CheckCircle} label="Passes" value={dashboard.total_passes || 0} subtext="Compliant checks" color="green" />
        <StatCard icon={AlertTriangle} label="RED Status" value={ragCounts.RED} subtext="Requirements at risk" color="red" />
        <StatCard icon={CheckCircle} label="GREEN Status" value={ragCounts.GREEN} subtext="Compliant requirements" color="green" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Bar Chart */}
        <div className="lg:col-span-2 bg-pci-card border border-pci-border rounded-xl p-6">
          <h3 className="text-white font-semibold mb-4">Violations by Requirement</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }}
              />
              <Bar dataKey="violations" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={barColors[entry.status] || '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="bg-pci-card border border-pci-border rounded-xl p-6">
          <h3 className="text-white font-semibold mb-4">RAG Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Requirements Table */}
      <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden">
        <div className="p-6 border-b border-pci-border">
          <h3 className="text-white font-semibold">All PCI DSS Requirements</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-pci-border">
                <th className="text-left p-4 text-xs text-slate-400 uppercase tracking-wider">Requirement</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase tracking-wider">Name</th>
                <th className="text-center p-4 text-xs text-slate-400 uppercase tracking-wider">Status</th>
                <th className="text-center p-4 text-xs text-slate-400 uppercase tracking-wider">Violations</th>
                <th className="text-left p-4 text-xs text-slate-400 uppercase tracking-wider">Systems Affected</th>
              </tr>
            </thead>
            <tbody>
              {dashboard.requirements?.map((req, i) => (
                <tr key={i} className="border-b border-pci-border/50 hover:bg-white/5 transition-colors animate-slide-in" style={{ animationDelay: `${i * 50}ms` }}>
                  <td className="p-4 font-mono text-sm text-blue-400">{req.requirement_id}</td>
                  <td className="p-4 text-sm text-slate-300 max-w-xs truncate">{req.requirement_name}</td>
                  <td className="p-4 text-center"><StatusBadge status={req.status} /></td>
                  <td className="p-4 text-center text-white font-semibold">{req.violations_count}</td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {req.systems_affected?.slice(0, 3).map((sys, j) => (
                        <span key={j} className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{sys}</span>
                      ))}
                      {(req.systems_affected?.length || 0) > 3 && (
                        <span className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-400">+{req.systems_affected.length - 3} more</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* CDE Segment Scores */}
      {dashboard.cde_segment_scores && Object.keys(dashboard.cde_segment_scores).length > 0 && (
        <div className="mt-6 bg-pci-card border border-pci-border rounded-xl p-6">
          <h3 className="text-white font-semibold mb-4">CDE Segment Risk Scores</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(dashboard.cde_segment_scores).map(([segment, score]) => (
              <div key={segment} className="bg-pci-dark/50 rounded-lg p-4 border border-pci-border/50">
                <p className="text-xs text-slate-400 truncate">{segment}</p>
                <p className={`text-2xl font-bold mt-1 ${score >= 7 ? 'text-red-400' : score >= 4 ? 'text-amber-400' : 'text-green-400'}`}>{score}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}