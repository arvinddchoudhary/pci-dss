from fastapi import FastAPI, HTTPException
from typing import Optional
from api.schemas import (
    ScanTrigger, ComplianceResponse, BatchScanRequest, BatchScanResponse,
    ApprovalAction
)
from agent_core.router import route_scan_request
from tools.dashboard import generate_dashboard
from tools.remediation import generate_remediation_workplan
from tools.report_generator import generate_qsa_report
from tools.evidence_collector import get_all_evidence, get_evidence_for_system, get_evidence_completeness_report
from tools.approval_queue import get_pending_approvals, get_all_approvals, review_approval
from vault.logger import get_audit_log, verify_chain_integrity
from vault.activity_logger import get_activity_log
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PCI DSS Compliance Agent",
    description="AI-powered PCI DSS v4.0 compliance monitoring, assessment, and remediation agent.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SCAN ENDPOINTS ===

@app.post("/scan", response_model=ComplianceResponse)
async def run_compliance_scan(trigger: ScanTrigger):
    """Run a single compliance scan against a system."""
    try:
        result = route_scan_request(trigger)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan/batch")
async def run_batch_scan(request: BatchScanRequest):
    """Run compliance scans against multiple systems at once."""
    results = []
    violations = 0
    passes = 0
    
    for trigger in request.systems:
        try:
            result = route_scan_request(trigger)
            result_dict = result.model_dump()
            result_dict["system_id"] = trigger.system_id
            results.append(result_dict)
            
            if result.status == "VIOLATION":
                violations += 1
            else:
                passes += 1
        except Exception as e:
            results.append({
                "system_id": trigger.system_id,
                "status": "ERROR",
                "reasoning": str(e)
            })
    
    return {
        "results": results,
        "summary": {
            "total": len(results),
            "violations": violations,
            "passes": passes,
            "errors": len(results) - violations - passes
        }
    }


# === DASHBOARD ===

@app.get("/dashboard")
async def get_compliance_dashboard():
    """
    Get real-time RAG (Red/Amber/Green) compliance dashboard.
    Shows status per PCI DSS requirement with risk scores per CDE segment.
    """
    try:
        return generate_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === REMEDIATION ===

@app.get("/remediation")
async def get_remediation_workplan():
    """
    Get prioritized remediation workplan with owner assignments, deadlines, and SLA tracking.
    """
    try:
        return generate_remediation_workplan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === QSA REPORT ===

@app.get("/report")
async def get_qsa_report(pci_version: str = "v4.0", organization: str = "Payments Corp"):
    """
    Generate a QSA audit-ready report with findings, evidence, and compensating controls.
    """
    try:
        return generate_qsa_report(pci_version, organization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === EVIDENCE ===

@app.get("/evidence")
async def get_evidence(system_id: Optional[str] = None):
    """
    Retrieve collected evidence packages. Optionally filter by system_id.
    """
    try:
        if system_id:
            return get_evidence_for_system(system_id)
        return get_all_evidence()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evidence/completeness")
async def get_evidence_completeness():
    """
    Check evidence completeness against QSA requirements.
    KPI Target: ≥ 85% of QSA evidence requests satisfied.
    """
    try:
        return get_evidence_completeness_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === HUMAN-IN-THE-LOOP APPROVALS ===

@app.get("/approvals")
async def get_approvals(status: Optional[str] = None):
    """
    Get approval queue. Filter by status: PENDING, APPROVED, REJECTED.
    """
    try:
        if status == "PENDING":
            return get_pending_approvals()
        return get_all_approvals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approvals/review")
async def review_violation(action: ApprovalAction):
    """
    Human reviews a pending violation. Approves or rejects remediation.
    Constraint C2: No auto-remediation without explicit human approval.
    """
    try:
        result = review_approval(
            violation_id=action.violation_id,
            action=action.action.value,
            reviewer=action.reviewer,
            comment=action.comment
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === AUDIT TRAIL ===

@app.get("/audit-log")
async def get_audit_trail(limit: int = 100):
    """
    Retrieve the immutable audit log with hash chain.
    Constraint C3: All agent actions must be logged immutably.
    """
    try:
        return get_audit_log(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-log/verify")
async def verify_audit_chain():
    """
    Verify the integrity of the hash chain in the audit log.
    Detects any tampering with historical records.
    """
    try:
        return verify_chain_integrity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent-activity")
async def get_agent_activity(limit: int = 100):
    """
    Retrieve the agent activity log — every action the AI agent took.
    The agent itself is auditable (Constraint C3).
    """
    try:
        return get_activity_log(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === HEALTH CHECK ===

@app.get("/health")
async def health_check():
    """Health check endpoint for uptime monitoring (SLA: 99.95%)."""
    return {
        "status": "healthy",
        "service": "PCI DSS Compliance Agent",
        "version": "2.0.0",
        "pci_versions_supported": ["v4.0", "v3.2.1"]
    }