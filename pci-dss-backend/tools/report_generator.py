"""
QSA Audit-Ready Report Generator.
KPI Target: QSA accepts agent-generated report with < 10% manual correction.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from collections import defaultdict

AUDIT_LOG = os.path.join(os.path.dirname(__file__), '..', 'vault', 'audit_log.jsonl')
EVIDENCE_STORE = os.path.join(os.path.dirname(__file__), '..', 'vault', 'evidence', 'evidence_packages.jsonl')

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


def generate_qsa_report(pci_version: str = "v4.0", organization: str = "Payments Corp") -> dict:
    """
    Generate a QSA-format audit report with findings, evidence references, and compensating controls.
    """
    audit_entries = _load_jsonl(AUDIT_LOG)
    evidence_entries = _load_jsonl(EVIDENCE_STORE)
    
    # Group findings by requirement
    req_findings = defaultdict(lambda: {"violations": [], "passes": 0, "evidence_hashes": []})
    
    cde_systems = set()
    
    for entry in audit_entries:
        system_id = entry.get("system_id", "unknown")
        cde_systems.add(system_id)
        
        rule = entry.get("violated_rule", "") or ""
        req_key = _map_to_requirement(rule)
        
        if entry.get("status") == "VIOLATION":
            req_findings[req_key]["violations"].append({
                "system_id": system_id,
                "rule": rule,
                "reasoning": entry.get("reasoning", ""),
                "risk_score": entry.get("risk_score"),
                "ticket_id": entry.get("ticket_id"),
                "timestamp": entry.get("timestamp")
            })
        else:
            req_findings[req_key]["passes"] += 1
    
    # Map evidence to requirements
    evidence_by_req = defaultdict(list)
    for ev in evidence_entries:
        req = ev.get("pci_requirement", "")
        req_key = _map_to_requirement(req)
        evidence_by_req[req_key].append(ev.get("hash", "")[:12])
    
    # Build report sections
    sections = []
    violation_count = 0
    pass_count = 0
    
    for req_id, req_name in PCI_REQUIREMENTS.items():
        data = req_findings.get(req_id, {"violations": [], "passes": 0})
        violations = data["violations"]
        passes = data["passes"]
        evidence_refs = evidence_by_req.get(req_id, [])
        
        if violations:
            status = "NOT COMPLIANT"
            violation_count += len(violations)
            findings = [
                f"[{v['system_id']}] {v['rule']}: {v['reasoning']} (Risk: {v['risk_score']}, Ticket: {v['ticket_id']})"
                for v in violations
            ]
        elif passes > 0:
            status = "COMPLIANT"
            pass_count += passes
            findings = [f"All assessed controls for {req_id} passed successfully."]
        else:
            status = "NOT ASSESSED"
            findings = [f"No systems assessed against {req_id} during this period."]
        
        sections.append({
            "requirement_id": req_id,
            "requirement_name": req_name,
            "status": status,
            "findings": findings,
            "evidence_refs": evidence_refs,
            "compensating_controls": None
        })
    
    # Determine overall status
    non_compliant = [s for s in sections if s["status"] == "NOT COMPLIANT"]
    if non_compliant:
        overall_status = "NOT COMPLIANT"
    elif any(s["status"] == "NOT ASSESSED" for s in sections):
        overall_status = "PARTIALLY ASSESSED"
    else:
        overall_status = "COMPLIANT"
    
    summary = (
        f"PCI DSS {pci_version} assessment for {organization}. "
        f"Total violations found: {violation_count}. "
        f"Total passes: {pass_count}. "
        f"Requirements not compliant: {len(non_compliant)}/{len(PCI_REQUIREMENTS)}. "
        f"CDE systems in scope: {len(cde_systems)}. "
        f"Overall status: {overall_status}."
    )
    
    return {
        "report_id": f"QSA-{uuid.uuid4().hex[:8].upper()}",
        "pci_version": pci_version,
        "assessment_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "assessor": "PCI DSS Compliance Agent v1.0",
        "organization": organization,
        "cde_scope": list(cde_systems),
        "overall_status": overall_status,
        "sections": sections,
        "summary": summary,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


def _map_to_requirement(rule_str: str) -> str:
    if not rule_str:
        return "Req 12"
    for req_id in PCI_REQUIREMENTS:
        num = req_id.split(" ")[1]
        if f"Req {num}" in rule_str or f"Requirement {num}" in rule_str or f"{num}." in rule_str:
            return req_id
    return "Req 12"


def _load_jsonl(filepath: str) -> list:
    entries = []
    if not os.path.exists(filepath):
        return entries
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries