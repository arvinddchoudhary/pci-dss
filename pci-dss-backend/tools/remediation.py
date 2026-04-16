"""
Remediation Orchestrator — Prioritized remediation tasks with owner assignment, 
deadlines, and SLA tracking with escalation.
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta

RACI_PATH = os.path.join(os.path.dirname(__file__), '..', 'agent_core', 'raci_matrix.json')
AUDIT_LOG = os.path.join(os.path.dirname(__file__), '..', 'vault', 'audit_log.jsonl')


def _load_raci():
    with open(RACI_PATH, 'r') as f:
        return json.load(f)


def _severity_from_score(score: int) -> str:
    if score is None:
        return "MEDIUM"
    if score >= 9:
        return "CRITICAL"
    elif score >= 7:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    return "LOW"


def _sla_hours_from_severity(severity: str) -> int:
    return {
        "CRITICAL": 24,
        "HIGH": 48,
        "MEDIUM": 72,
        "LOW": 168  # 7 days
    }.get(severity, 72)


def generate_remediation_workplan() -> dict:
    """
    Generate a prioritized remediation workplan from all violations in the audit log.
    Assigns owners from RACI matrix, sets deadlines based on severity/SLA.
    """
    raci = _load_raci()
    entries = _load_audit_log()
    
    # Only process violations
    violations = [e for e in entries if e.get("status") == "VIOLATION"]
    
    tasks = []
    for entry in violations:
        risk_score = entry.get("risk_score") or 5
        severity = _severity_from_score(risk_score)
        sla_hours = _sla_hours_from_severity(severity)
        assigned_to = entry.get("assigned_to", "Cloud_Sec_Team")
        
        # Get owner from RACI
        team_info = raci.get(assigned_to, {})
        owner = team_info.get("lead", "Unassigned")
        
        # Override SLA from RACI if available
        team_sla = team_info.get("sla_hours")
        if team_sla and team_sla < sla_hours:
            sla_hours = team_sla
        
        created_at = entry.get("timestamp", datetime.now(timezone.utc).isoformat())
        try:
            created_dt = datetime.fromisoformat(created_at)
        except (ValueError, TypeError):
            created_dt = datetime.now(timezone.utc)
        
        deadline_dt = created_dt + timedelta(hours=sla_hours)
        
        # Check if escalation needed (past SLA)
        now = datetime.now(timezone.utc)
        is_escalated = now > deadline_dt
        
        task = {
            "task_id": f"REM-{uuid.uuid4().hex[:6].upper()}",
            "system_id": entry.get("system_id", "unknown"),
            "violated_rule": entry.get("violated_rule"),
            "severity": severity,
            "assigned_to": assigned_to,
            "owner": owner,
            "deadline": deadline_dt.isoformat(),
            "status": "ESCALATED" if is_escalated else "OPEN",
            "ticket_id": entry.get("ticket_id"),
            "sla_hours": sla_hours,
            "created_at": created_at,
            "escalation_at": now.isoformat() if is_escalated else None,
            "reasoning": entry.get("reasoning")
        }
        tasks.append(task)
    
    # Sort by severity (CRITICAL first), then by risk score descending
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    tasks.sort(key=lambda t: (severity_order.get(t["severity"], 99), -(_sla_hours_from_severity(t["severity"]))))
    
    critical_count = sum(1 for t in tasks if t["severity"] == "CRITICAL")
    high_count = sum(1 for t in tasks if t["severity"] == "HIGH")
    
    return {
        "total_tasks": len(tasks),
        "critical_count": critical_count,
        "high_count": high_count,
        "escalated_count": sum(1 for t in tasks if t["status"] == "ESCALATED"),
        "tasks": tasks,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


def _load_audit_log() -> list:
    entries = []
    if not os.path.exists(AUDIT_LOG):
        return entries
    with open(AUDIT_LOG, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries