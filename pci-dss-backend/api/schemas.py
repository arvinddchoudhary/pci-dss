from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ScanTrigger(BaseModel):
    system_id: str = Field(..., description="The unique ID of the server to check")
    cloud_provider: str = Field(default="aws", description="aws, azure, or on-prem")
    pci_version: str = Field(default="v4.0", description="PCI DSS version to check against")
    config_override: Optional[str] = Field(None, description="Optional mock config for automated evaluation testing")
    cde_segment: Optional[str] = Field(default="default", description="CDE segment this system belongs to")

class ComplianceResponse(BaseModel):
    status: str = Field(..., description="Either 'PASS' or 'VIOLATION'")
    violated_rule: Optional[str] = Field(None, description="The specific PCI requirement broken")
    reasoning: Optional[str] = Field(None, description="The AI's explanation")
    risk_score: Optional[int] = Field(None, ge=1, le=10, description="Severity from 1 to 10")
    assigned_to: Optional[str] = Field(None, description="The RACI team assigned to fix this")
    ticket_id: Optional[str] = Field(None, description="The Jira ticket number created")

class BatchScanRequest(BaseModel):
    systems: List[ScanTrigger]

class BatchScanResponse(BaseModel):
    results: List[dict]
    summary: dict

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ApprovalRequest(BaseModel):
    violation_id: str
    system_id: str
    violated_rule: Optional[str]
    risk_score: Optional[int]
    reasoning: Optional[str]
    assigned_to: Optional[str]
    ticket_id: Optional[str]
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None

class ApprovalAction(BaseModel):
    violation_id: str
    action: ApprovalStatus  # APPROVED or REJECTED
    reviewer: str
    comment: Optional[str] = None

class EvidencePackage(BaseModel):
    system_id: str
    pci_requirement: Optional[str]
    evidence_type: str
    collected_at: str
    config_snapshot: str
    scan_result: str
    hash: str
    metadata: dict = {}

class DashboardRequirement(BaseModel):
    requirement_id: str
    requirement_name: str
    status: str  # RED, AMBER, GREEN
    violations_count: int
    last_checked: Optional[str]
    systems_affected: List[str]

class DashboardResponse(BaseModel):
    overall_risk_score: float
    total_systems: int
    total_violations: int
    total_passes: int
    requirements: List[DashboardRequirement]
    cde_segment_scores: dict
    generated_at: str

class RemediationTask(BaseModel):
    task_id: str
    system_id: str
    violated_rule: Optional[str]
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    assigned_to: Optional[str]
    owner: Optional[str]
    deadline: str
    status: str  # OPEN, IN_PROGRESS, RESOLVED, ESCALATED
    ticket_id: Optional[str]
    sla_hours: int
    created_at: str
    escalation_at: Optional[str] = None

class RemediationWorkplan(BaseModel):
    total_tasks: int
    critical_count: int
    high_count: int
    tasks: List[RemediationTask]
    generated_at: str

class QSAReportSection(BaseModel):
    requirement_id: str
    requirement_name: str
    status: str
    findings: List[str]
    evidence_refs: List[str]
    compensating_controls: Optional[str] = None

class QSAReport(BaseModel):
    report_id: str
    pci_version: str
    assessment_date: str
    assessor: str
    organization: str
    cde_scope: List[str]
    overall_status: str
    sections: List[QSAReportSection]
    summary: str
    generated_at: str

class AgentActivityEntry(BaseModel):
    timestamp: str
    agent_name: str
    action: str
    system_id: Optional[str]
    details: str
    duration_ms: Optional[float] = None