import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ====== SCAN ENDPOINTS ======
export const runSingleScan = async (payload) => {
  const response = await api.post('/scan', payload);
  return response.data;
};

export const runBatchScan = async (systems) => {
  const response = await api.post('/scan/batch', { systems });
  return response.data;
};

// ====== DASHBOARD ======
export const getDashboard = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

// ====== REMEDIATION ======
export const getRemediation = async () => {
  const response = await api.get('/remediation');
  return response.data;
};

// ====== QSA REPORT ======
export const getQSAReport = async (pciVersion = 'v4.0', organization = 'Payments Corp') => {
  const response = await api.get('/report', {
    params: { pci_version: pciVersion, organization },
  });
  return response.data;
};

// ====== EVIDENCE ======
export const getAllEvidence = async (systemId = null) => {
  const params = systemId ? { system_id: systemId } : {};
  const response = await api.get('/evidence', { params });
  return response.data;
};

export const getEvidenceCompleteness = async () => {
  const response = await api.get('/evidence/completeness');
  return response.data;
};

// ====== APPROVALS ======
export const getApprovals = async (status = null) => {
  const params = status ? { status } : {};
  const response = await api.get('/approvals', { params });
  return response.data;
};

export const reviewApproval = async (violationId, action, reviewer, comment = '') => {
  const response = await api.post('/approvals/review', {
    violation_id: violationId,
    action,
    reviewer,
    comment,
  });
  return response.data;
};

// ====== AUDIT LOG ======
export const getAuditLog = async (limit = 100) => {
  const response = await api.get('/audit-log', { params: { limit } });
  return response.data;
};

export const verifyAuditChain = async () => {
  const response = await api.get('/audit-log/verify');
  return response.data;
};

// ====== AGENT ACTIVITY ======
export const getAgentActivity = async (limit = 100) => {
  const response = await api.get('/agent-activity', { params: { limit } });
  return response.data;
};

// ====== HEALTH ======
export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;