import hashlib
import json
import os
from datetime import datetime, timezone

os.makedirs(os.path.dirname(__file__) or '.', exist_ok=True)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'audit_log.jsonl')

# In-memory previous hash for chain continuity
_previous_hash = None

def _get_last_hash() -> str:
    """Read the last hash from the log file to continue the chain."""
    global _previous_hash
    if _previous_hash:
        return _previous_hash
    
    last_hash = "GENESIS"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        last_hash = entry.get('hash', last_hash)
                    except json.JSONDecodeError:
                        continue
    return last_hash


def log_decision(decision: dict) -> str:
    """Log decision with hash chain — each record references previous hash for tamper detection."""
    global _previous_hash
    
    previous_hash = _get_last_hash()
    
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'system_id': decision.get('system_id', 'unknown'),
        'status': decision.get('status'),
        'violated_rule': decision.get('violated_rule'),
        'risk_score': decision.get('risk_score'),
        'ticket_id': decision.get('ticket_id'),
        'reasoning': decision.get('reasoning'),
        'previous_hash': previous_hash,
    }
    
    record_str = json.dumps(record, sort_keys=True)
    record_hash = hashlib.sha256(record_str.encode()).hexdigest()
    record['hash'] = record_hash
    
    _previous_hash = record_hash
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')
        
    print(f"🔒 Vault: Decision logged with hash chain {record_hash[:8]}... (prev: {previous_hash[:8]}...)")
    return record_hash


def verify_chain_integrity() -> dict:
    """Verify the entire hash chain is intact — detect any tampering."""
    if not os.path.exists(LOG_FILE):
        return {"valid": True, "entries": 0, "message": "No log file found."}
    
    entries = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    if not entries:
        return {"valid": True, "entries": 0, "message": "Log file is empty."}
    
    broken_links = []
    
    for i, entry in enumerate(entries):
        stored_hash = entry.get('hash')
        
        # Reconstruct the record without the hash field to verify
        verify_record = {k: v for k, v in entry.items() if k != 'hash'}
        verify_str = json.dumps(verify_record, sort_keys=True)
        computed_hash = hashlib.sha256(verify_str.encode()).hexdigest()
        
        if stored_hash != computed_hash:
            broken_links.append({
                "entry_index": i,
                "issue": "Hash mismatch — record may have been tampered with",
                "stored": stored_hash[:16],
                "computed": computed_hash[:16]
            })
        
        # Check chain link (for entries that have previous_hash)
        if i > 0 and 'previous_hash' in entry:
            expected_prev = entries[i - 1].get('hash')
            actual_prev = entry.get('previous_hash')
            if expected_prev and actual_prev and expected_prev != actual_prev:
                broken_links.append({
                    "entry_index": i,
                    "issue": "Chain break — previous_hash does not match prior entry's hash"
                })
    
    return {
        "valid": len(broken_links) == 0,
        "entries": len(entries),
        "broken_links": broken_links,
        "message": "Chain intact ✅" if not broken_links else f"Chain broken at {len(broken_links)} points ❌"
    }


def get_audit_log(limit: int = 100) -> list:
    """Retrieve recent audit log entries."""
    entries = []
    if not os.path.exists(LOG_FILE):
        return entries
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return entries[-limit:]