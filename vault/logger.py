import hashlib
import json
import os
from datetime import datetime, timezone

os.makedirs(os.path.dirname(__file__), exist_ok=True)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'audit_log.jsonl')

def log_decision(decision: dict) -> str:
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'system_id': decision.get('system_id', 'unknown'),
        'status': decision.get('status'),
        'violated_rule': decision.get('violated_rule'),
        'risk_score': decision.get('risk_score'),
        'ticket_id': decision.get('ticket_id'),
        'reasoning': decision.get('reasoning'),
    }
    
    record_str = json.dumps(record, sort_keys=True)
    record_hash = hashlib.sha256(record_str.encode()).hexdigest()
    record['hash'] = record_hash
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')
        
    print(f"🔒 Vault: Decision logged immutably with hash {record_hash[:8]}...")
    return record_hash