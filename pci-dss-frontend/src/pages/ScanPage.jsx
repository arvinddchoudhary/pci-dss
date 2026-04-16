import React, { useState } from 'react';
import { Scan, Play, Plus, Trash2, Zap } from 'lucide-react';
import { runSingleScan, runBatchScan } from '../services/api';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const QUICK_SCANS = [
  { system_id: 'prod-db-01', cloud_provider: 'aws', pci_version: 'v4.0', label: 'Production DB (Known Violation)' },
  { system_id: 'secure-db-02', cloud_provider: 'aws', pci_version: 'v4.0', label: 'Secure DB (Should Pass)' },
  { system_id: 'prod-iam-01', cloud_provider: 'aws', pci_version: 'v4.0', label: 'Prod IAM User (No MFA)' },
  { system_id: 'secure-iam-02', cloud_provider: 'aws', pci_version: 'v4.0', label: 'Secure IAM User' },
];

export default function ScanPage() {
  const [mode, setMode] = useState('single'); // single or batch
  const [form, setForm] = useState({
    system_id: '',
    cloud_provider: 'aws',
    pci_version: 'v4.0',
    config_override: '',
  });
  const [batchSystems, setBatchSystems] = useState([{ system_id: '', cloud_provider: 'aws', pci_version: 'v4.0', config_override: '' }]);
  const [results, setResults] = useState(null);
  const [scanning, setScanning] = useState(false);

  const handleSingleScan = async (e) => {
    e.preventDefault();
    setScanning(true);
    setResults(null);
    try {
      const payload = { ...form };
      if (!payload.config_override) delete payload.config_override;
      const data = await runSingleScan(payload);
      setResults({ type: 'single', data });
    } catch (err) {
      setResults({ type: 'error', data: err.response?.data?.detail || err.message });
    } finally {
      setScanning(false);
    }
  };

  const handleBatchScan = async (e) => {
    e.preventDefault();
    setScanning(true);
    setResults(null);
    try {
      const systems = batchSystems.filter(s => s.system_id).map(s => {
        const payload = { ...s };
        if (!payload.config_override) delete payload.config_override;
        return payload;
      });
      const data = await runBatchScan(systems);
      setResults({ type: 'batch', data });
    } catch (err) {
      setResults({ type: 'error', data: err.response?.data?.detail || err.message });
    } finally {
      setScanning(false);
    }
  };

  const handleQuickScan = async (preset) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await runSingleScan(preset);
      setResults({ type: 'single', data });
    } catch (err) {
      setResults({ type: 'error', data: err.response?.data?.detail || err.message });
    } finally {
      setScanning(false);
    }
  };

  const addBatchRow = () => {
    setBatchSystems([...batchSystems, { system_id: '', cloud_provider: 'aws', pci_version: 'v4.0', config_override: '' }]);
  };

  const removeBatchRow = (index) => {
    setBatchSystems(batchSystems.filter((_, i) => i !== index));
  };

  const updateBatchRow = (index, field, value) => {
    const updated = [...batchSystems];
    updated[index][field] = value;
    setBatchSystems(updated);
  };

  return (
    <div className="animate-fade-in">
      <PageHeader
        icon={Scan}
        title="Compliance Scanner"
        subtitle="Run PCI DSS compliance scans against infrastructure, IAM, network, and encryption systems"
      />

      {/* Quick Scans */}
      <div className="bg-pci-card border border-pci-border rounded-xl p-6 mb-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" /> Quick Scans (Pre-configured)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {QUICK_SCANS.map((preset, i) => (
            <button
              key={i}
              onClick={() => handleQuickScan(preset)}
              disabled={scanning}
              className="p-3 bg-pci-dark/50 border border-pci-border/50 rounded-lg hover:border-blue-500/30 hover:bg-blue-500/5 transition-all text-left"
            >
              <p className="text-sm font-medium text-white">{preset.system_id}</p>
              <p className="text-xs text-slate-400 mt-1">{preset.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('single')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'single' ? 'bg-blue-500 text-white' : 'bg-pci-card border border-pci-border text-slate-400 hover:text-white'}`}
        >
          Single Scan
        </button>
        <button
          onClick={() => setMode('batch')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'batch' ? 'bg-blue-500 text-white' : 'bg-pci-card border border-pci-border text-slate-400 hover:text-white'}`}
        >
          Batch Scan
        </button>
      </div>

      {/* Single Scan Form */}
      {mode === 'single' && (
        <form onSubmit={handleSingleScan} className="bg-pci-card border border-pci-border rounded-xl p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-slate-400 mb-2 uppercase tracking-wider">System ID *</label>
              <input
                type="text"
                value={form.system_id}
                onChange={(e) => setForm({ ...form, system_id: e.target.value })}
                placeholder="e.g., prod-db-01"
                className="w-full bg-pci-dark border border-pci-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Cloud Provider</label>
              <select
                value={form.cloud_provider}
                onChange={(e) => setForm({ ...form, cloud_provider: e.target.value })}
                className="w-full bg-pci-dark border border-pci-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none"
              >
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
                <option value="on-prem">On-Prem</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-2 uppercase tracking-wider">PCI Version</label>
              <select
                value={form.pci_version}
                onChange={(e) => setForm({ ...form, pci_version: e.target.value })}
                className="w-full bg-pci-dark border border-pci-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none"
              >
                <option value="v4.0">v4.0</option>
                <option value="v3.2.1">v3.2.1</option>
              </select>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Config Override (Optional — for testing)</label>
            <textarea
              value={form.config_override}
              onChange={(e) => setForm({ ...form, config_override: e.target.value })}
              placeholder="e.g., RDS postgres-14. PubliclyAccessible: True. StorageEncrypted: False."
              className="w-full bg-pci-dark border border-pci-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-blue-500 focus:outline-none h-20 resize-none"
            />
          </div>
          <button
            type="submit"
            disabled={scanning}
            className="flex items-center gap-2 px-6 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 font-medium"
          >
            <Play className="w-4 h-4" />
            {scanning ? 'Scanning...' : 'Run Scan'}
          </button>
        </form>
      )}

      {/* Batch Scan Form */}
      {mode === 'batch' && (
        <form onSubmit={handleBatchScan} className="bg-pci-card border border-pci-border rounded-xl p-6 mb-6">
          {batchSystems.map((sys, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-3 animate-slide-in">
              <input
                type="text" placeholder="System ID"
                value={sys.system_id}
                onChange={(e) => updateBatchRow(i, 'system_id', e.target.value)}
                className="bg-pci-dark border border-pci-border rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <select value={sys.cloud_provider} onChange={(e) => updateBatchRow(i, 'cloud_provider', e.target.value)}
                className="bg-pci-dark border border-pci-border rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none">
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
              </select>
              <select value={sys.pci_version} onChange={(e) => updateBatchRow(i, 'pci_version', e.target.value)}
                className="bg-pci-dark border border-pci-border rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none">
                <option value="v4.0">v4.0</option>
                <option value="v3.2.1">v3.2.1</option>
              </select>
              <input
                type="text" placeholder="Config Override (optional)"
                value={sys.config_override}
                onChange={(e) => updateBatchRow(i, 'config_override', e.target.value)}
                className="bg-pci-dark border border-pci-border rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <button type="button" onClick={() => removeBatchRow(i)} className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors self-center">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          <div className="flex gap-3 mt-4">
            <button type="button" onClick={addBatchRow} className="flex items-center gap-2 px-4 py-2 border border-dashed border-pci-border rounded-lg text-slate-400 hover:text-white hover:border-blue-500/30 text-sm">
              <Plus className="w-4 h-4" /> Add System
            </button>
            <button type="submit" disabled={scanning}
              className="flex items-center gap-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 font-medium text-sm">
              <Play className="w-4 h-4" /> {scanning ? 'Scanning...' : `Scan ${batchSystems.filter(s => s.system_id).length} Systems`}
            </button>
          </div>
        </form>
      )}

      {scanning && <LoadingSpinner message="Running compliance scan..." />}

      {/* Results */}
      {results && results.type === 'single' && (
        <div className="bg-pci-card border border-pci-border rounded-xl p-6 animate-fade-in">
          <h3 className="text-white font-semibold mb-4">Scan Result</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div><span className="text-xs text-slate-400">Status</span><div className="mt-1"><StatusBadge status={results.data.status} size="lg" /></div></div>
            <div><span className="text-xs text-slate-400">Rule Violated</span><p className="text-white font-mono mt-1">{results.data.violated_rule || 'None'}</p></div>
            <div><span className="text-xs text-slate-400">Risk Score</span><p className={`text-2xl font-bold mt-1 ${(results.data.risk_score || 0) >= 7 ? 'text-red-400' : 'text-green-400'}`}>{results.data.risk_score || 'N/A'}</p></div>
            <div><span className="text-xs text-slate-400">Ticket</span><p className="text-blue-400 font-mono mt-1">{results.data.ticket_id || 'N/A'}</p></div>
          </div>
          <div className="bg-pci-dark/50 rounded-lg p-4">
            <span className="text-xs text-slate-400">Reasoning</span>
            <p className="text-slate-300 text-sm mt-1">{results.data.reasoning || 'No reasoning provided'}</p>
          </div>
          {results.data.assigned_to && (
            <div className="mt-3">
              <span className="text-xs text-slate-400">Assigned to: </span>
              <span className="text-purple-400 font-medium">{results.data.assigned_to}</span>
            </div>
          )}
        </div>
      )}

      {results && results.type === 'batch' && (
        <div className="bg-pci-card border border-pci-border rounded-xl overflow-hidden animate-fade-in">
          <div className="p-6 border-b border-pci-border flex items-center justify-between">
            <h3 className="text-white font-semibold">Batch Results</h3>
            <div className="flex gap-4 text-sm">
              <span className="text-green-400">✅ {results.data.summary?.passes || 0} Passed</span>
              <span className="text-red-400">❌ {results.data.summary?.violations || 0} Violations</span>
            </div>
          </div>
          <div className="divide-y divide-pci-border/50">
            {results.data.results?.map((r, i) => (
              <div key={i} className="p-4 hover:bg-white/5 transition-colors flex items-center gap-4">
                <StatusBadge status={r.status} />
                <span className="font-mono text-sm text-blue-400 w-32">{r.system_id}</span>
                <span className="text-sm text-slate-400 flex-1 truncate">{r.reasoning}</span>
                <span className="font-mono text-xs text-slate-500">{r.violated_rule || '—'}</span>
                <span className="text-sm text-slate-400">{r.ticket_id || '—'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {results && results.type === 'error' && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 animate-fade-in">
          <p className="text-red-400 font-medium">Scan Failed</p>
          <p className="text-red-300/70 text-sm mt-1">{results.data}</p>
        </div>
      )}
    </div>
  );
}