"""
Compliance Dashboard — Real-time RAG (Red/Amber/Green) status per PCI DSS requirement.
"""

import json
import os
from datetime import datetime, timezone
from collections import defaultdict

AUDIT_LOG = os.path.join(os.path.dirname(__file__), '..', 'vault', 'audit_log.jsonl')

# PCI DSS v4.0 requirement names
PCI_REQUIREMENTS = {
    "Req 1": "Install and Maintain Network Security Controls",
    "Req 2": "Apply Secure Configurations to All System Components",
    "Req 3": "Protect Stored Account Data",
    "Req 4": "Protect Cardholder Data with Strong Cryptography During Transmission",
    "Req 5": "Protect All Systems and Networks from Malicious Software",
    "Req 6": "Develop and Maintain Secure Systems and Software",
    "Req 7": "Restrict Access to System Components and Cardholder Data by Business Need to Know",
    "Req 8": "Identify Users and Authenticate Access to System Components",
    "Req 9": "Restrict Physical Access to Cardholder Data",
    "Req 10": "Log and Monitor All Access to System Components and Cardholder Data",
    "Req 11": "Test Security of Systems and Networks Regularly",
    "Req 12": "Support Information Security with Organizational Policies and Programs",
}


def generate_dashboard() -> dict:
    """Generate a real-time compliance dashboard with RAG status."""
    entries = _load_audit_log()
    
    # Track violations per requirement
    req_violations = defaultdict(lambda: {"violations": 0, "passes": 0, "systems": set(), "last_checked": None})
    cde_scores = defaultdict(list)
    
    total_violations = 0
    total_passes = 0
    all_risk_scores = []
    
    for entry in entries:
        status = entry.get("status")
        rule = entry.get("violated_rule", "") or ""
        system_id = entry.get("system_id", "unknown")
        risk_score = entry.get("risk_score")
        timestamp = entry.get("timestamp")
        
        # Map the violated rule to a top-level requirement
        req_key = _map_to_requirement(rule)
        
        if status == "VIOLATION":
            total_violations += 1
            req_violations[req_key]["violations"] += 1
            req_violations[req_key]["systems"].add(system_id)
            if risk_score:
                all_risk_scores.append(risk_score)
                cde_scores[system_id].append(risk_score)
        elif status == "PASS":
            total_passes += 1
            req_violations[req_key]["passes"] += 1
        
        req_violations[req_key]["last_checked"] = timestamp
    
    # Build requirement statuses
    requirements = []
    for req_id, req_name in PCI_REQUIREMENTS.items():
        data = req_violations.get(req_id, {"violations": 0, "passes": 0, "systems": set(), "last_checked": None})
        v_count = data["violations"]
        
        # RAG logic
        if v_count == 0:
            rag_status = "GREEN"
        elif v_count <= 2:
            rag_status = "AMBER"
        else:
            rag_status = "RED"
        
        requirements.append({
            "requirement_id": req_id,
            "requirement_name": req_name,
            "status": rag_status,
            "violations_count": v_count,
            "last_checked": data["last_checked"],
            "systems_affected": list(data["systems"])
        })
    
    # CDE segment scores
    segment_scores = {}
    for system_id, scores in cde_scores.items():
        segment_scores[system_id] = round(sum(scores) / len(scores), 1) if scores else 0
    
    overall_risk = round(sum(all_risk_scores) / len(all_risk_scores), 1) if all_risk_scores else 0
    
    return {
        "overall_risk_score": overall_risk,
        "total_systems": len(set(e.get("system_id") for e in entries)),
        "total_violations": total_violations,
        "total_passes": total_passes,
        "requirements": requirements,
        "cde_segment_scores": segment_scores,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


def _map_to_requirement(rule_str: str) -> str:
    """Map a specific rule (e.g., 'Req 8.4.2') to its top-level requirement ('Req 8')."""
    if not rule_str:
        return "Req 12"  # Default to organizational policies
    
    for req_id in PCI_REQUIREMENTS:
        # Match "Req 8" in "Req 8.4.2" or "Requirement 8.4"
        num = req_id.split(" ")[1]
        if f"Req {num}" in rule_str or f"Requirement {num}" in rule_str or f"{num}." in rule_str:
            return req_id
    
    return "Req 12"  # Unmapped


def _load_audit_log() -> list:
    """Load all audit log entries."""
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