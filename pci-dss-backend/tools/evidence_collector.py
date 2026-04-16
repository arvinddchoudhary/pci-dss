import hashlib
import json
import os
from datetime import datetime, timezone

EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), '..', 'vault', 'evidence')
os.makedirs(EVIDENCE_DIR, exist_ok=True)

EVIDENCE_STORE = os.path.join(EVIDENCE_DIR, 'evidence_packages.jsonl')


def collect_evidence(system_id: str, pci_requirement: str, config_snapshot: str,
                     scan_result: dict, evidence_type: str = "automated_scan") -> dict:
    """
    Collect and package evidence mapped to a PCI control.
    Evidence is hashed for immutability (per Risk mitigation: "immutable storage + hash chain").
    """
    
    evidence = {
        "system_id": system_id,
        "pci_requirement": pci_requirement,
        "evidence_type": evidence_type,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "config_snapshot": config_snapshot,
        "scan_result": json.dumps(scan_result) if isinstance(scan_result, dict) else str(scan_result),
        "metadata": {
            "collector": "pci-dss-agent-v1.0",
            "method": "api_read_only",
            "source": "automated"
        }
    }
    
    # Create immutable hash of the evidence
    evidence_str = json.dumps(evidence, sort_keys=True)
    evidence["hash"] = hashlib.sha256(evidence_str.encode()).hexdigest()
    
    # Persist to evidence store
    with open(EVIDENCE_STORE, 'a') as f:
        f.write(json.dumps(evidence) + '\n')
    
    print(f"📦 Evidence collected for {system_id} | Req {pci_requirement} | Hash: {evidence['hash'][:8]}...")
    return evidence


def get_evidence_for_system(system_id: str) -> list:
    """Retrieve all evidence packages for a given system."""
    evidence_list = []
    if not os.path.exists(EVIDENCE_STORE):
        return evidence_list
    
    with open(EVIDENCE_STORE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("system_id") == system_id:
                        evidence_list.append(entry)
                except json.JSONDecodeError:
                    continue
    
    return evidence_list


def get_evidence_for_requirement(pci_requirement: str) -> list:
    """Retrieve all evidence for a specific PCI requirement."""
    evidence_list = []
    if not os.path.exists(EVIDENCE_STORE):
        return evidence_list
    
    with open(EVIDENCE_STORE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("pci_requirement") == pci_requirement:
                        evidence_list.append(entry)
                except json.JSONDecodeError:
                    continue
    
    return evidence_list


def get_all_evidence(limit: int = 200) -> list:
    """Retrieve all evidence packages."""
    evidence_list = []
    if not os.path.exists(EVIDENCE_STORE):
        return evidence_list
    
    with open(EVIDENCE_STORE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    evidence_list.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return evidence_list[-limit:]


def get_evidence_completeness_report() -> dict:
    """
    Calculate evidence completeness percentage.
    KPI target: ≥ 85% of QSA evidence requests satisfied.
    """
    # Key PCI requirements that need evidence
    required_evidence = [
        "Req 1.3.2", "Req 2.2.2", "Req 3.4.1", "Req 4.2.1",
        "Req 5.3.1", "Req 6.3.3", "Req 7.2.1", "Req 8.4.2",
        "Req 9.4.1", "Req 10.2.1", "Req 11.4.1", "Req 12.1.1"
    ]
    
    all_evidence = get_all_evidence()
    covered_reqs = set()
    
    for ev in all_evidence:
        req = ev.get("pci_requirement", "")
        for required_req in required_evidence:
            if required_req in req:
                covered_reqs.add(required_req)
    
    completeness = (len(covered_reqs) / len(required_evidence)) * 100 if required_evidence else 0
    
    return {
        "total_required": len(required_evidence),
        "covered": len(covered_reqs),
        "missing": [r for r in required_evidence if r not in covered_reqs],
        "completeness_pct": round(completeness, 1),
        "meets_kpi": completeness >= 85.0
    }