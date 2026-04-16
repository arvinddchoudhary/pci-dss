import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Scan, Shield, FileText, Package,
  UserCheck, ScrollText, Activity, Heart, ChevronRight
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard', description: 'RAG Status Overview' },
  { path: '/scan', icon: Scan, label: 'Scan', description: 'Run Compliance Scans' },
  { path: '/remediation', icon: Shield, label: 'Remediation', description: 'Workplan & SLAs' },
  { path: '/report', icon: FileText, label: 'QSA Report', description: 'Audit-Ready Report' },
  { path: '/evidence', icon: Package, label: 'Evidence', description: 'Evidence Packages' },
  { path: '/approvals', icon: UserCheck, label: 'Approvals', description: 'Human-in-the-Loop' },
  { path: '/audit-log', icon: ScrollText, label: 'Audit Log', description: 'Hash Chain Log' },
  { path: '/activity', icon: Activity, label: 'Agent Activity', description: 'Agent Actions' },
  { path: '/health', icon: Heart, label: 'Health', description: 'System Status' },
];

export default function Sidebar() {
  return (
    <aside className="w-72 bg-pci-card border-r border-pci-border min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-pci-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">PCI DSS</h1>
            <p className="text-xs text-slate-400">Compliance Agent v2.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{item.label}</p>
              <p className="text-xs text-slate-500 truncate">{item.description}</p>
            </div>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-pci-border">
        <div className="text-xs text-slate-500 text-center">
          PCI DSS v4.0 + v3.2.1
          <br />
          Built for QSA Compliance
        </div>
      </div>
    </aside>
  );
}