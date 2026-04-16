"""
Human-in-the-Loop Approval System
Per Constraint C2: No auto-remediation without explicit human approval.
Per Architecture: High-severity violations require human confirmation.
"""

import json
import os
import uuid
from datetime import datetime, timezone

APPROVAL_FILE = os.path.join(os.path.dirname(__file__), '..', 'vault', 'approval_queue.jsonl')
os.makedirs(os.path.dirname(APPROVAL_FILE), exist_ok=True)


def submit_for_approval(system_id: str, violated_rule: str, risk_score: int,
                        reasoning: str, assigned_to: str, ticket_id: str = None) -> dict:
    """
    Submit a high-severity violation for human review before remediation.
    Threshold: risk_score >= 8 requires human approval.
    """
    violation_id = f"VIO-{uuid.uuid4().hex[:8].upper()}"
    
    approval_request = {
        "violation_id": violation_id,
        "system_id": system_id,
        "violated_rule": violated_rule,
        "risk_score": risk_score,
        "reasoning": reasoning,
        "assigned_to": assigned_to,
        "ticket_id": ticket_id,
        "status": "PENDING",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_by": None,
        "reviewed_at": None,
        "comment": None
    }
    
    with open(APPROVAL_FILE, 'a') as f:
        f.write(json.dumps(approval_request) + '\n')
    
    print(f"⏳ Approval requested: {violation_id} for {system_id} (Risk: {risk_score})")
    return approval_request


def review_approval(violation_id: str, action: str, reviewer: str, comment: str = None) -> dict:
    """
    Human reviews a pending approval. action = 'APPROVED' or 'REJECTED'.
    """
    entries = _load_all_approvals()
    updated = None
    
    for entry in entries:
        if entry["violation_id"] == violation_id:
            if entry["status"] != "PENDING":
                return {"error": f"Violation {violation_id} already {entry['status']}"}
            entry["status"] = action
            entry["reviewed_by"] = reviewer
            entry["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            entry["comment"] = comment
            updated = entry
            break
    
    if not updated:
        return {"error": f"Violation {violation_id} not found"}
    
    # Rewrite the file with updated entries
    with open(APPROVAL_FILE, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"{'✅' if action == 'APPROVED' else '❌'} {violation_id} {action} by {reviewer}")
    return updated


def get_pending_approvals() -> list:
    """Get all violations pending human review."""
    entries = _load_all_approvals()
    return [e for e in entries if e["status"] == "PENDING"]


def get_all_approvals() -> list:
    """Get full approval history (audit trail per Constraint C3)."""
    return _load_all_approvals()


def _load_all_approvals() -> list:
    """Load all approval entries from file."""
    entries = []
    if not os.path.exists(APPROVAL_FILE):
        return entries
    
    with open(APPROVAL_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries