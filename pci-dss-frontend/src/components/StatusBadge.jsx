import React from 'react';

const statusStyles = {
  VIOLATION: 'status-red',
  RED: 'status-red',
  CRITICAL: 'status-red',
  ESCALATED: 'status-red',
  NOT_COMPLIANT: 'status-red',
  'NOT COMPLIANT': 'status-red',

  AMBER: 'status-amber',
  WARNING: 'status-amber',
  HIGH: 'status-amber',
  PENDING: 'status-amber',
  OPEN: 'status-amber',
  'PARTIALLY ASSESSED': 'status-amber',

  PASS: 'status-green',
  GREEN: 'status-green',
  COMPLIANT: 'status-green',
  APPROVED: 'status-green',
  RESOLVED: 'status-green',
  LOW: 'status-green',

  MEDIUM: 'status-blue',
  INFO: 'status-blue',
  'NOT ASSESSED': 'status-purple',
  REJECTED: 'status-purple',
};

export default function StatusBadge({ status, size = 'sm' }) {
  const style = statusStyles[status] || 'status-blue';
  const sizeClass = size === 'lg' ? 'px-4 py-2 text-sm' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`${style} ${sizeClass} rounded-full font-semibold inline-flex items-center gap-1`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}